import { GoogleGenerativeAI } from "@google/generative-ai";
import { Article } from "./utils/dedup.js";

export interface ArticleWithRank extends Article {
  score: number;
  ai_summary: string;
  ai_tags: string[];
}

const API_KEY = process.env.GEMINI_API_KEY;
const DELAY_MS = 1000;
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 2000;

/**
 * 延迟执行
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 清理 Gemini 返回的 JSON（可能被 markdown 代码块包裹）
 */
function cleanJsonResponse(text: string): string {
  // 移除 markdown 代码块标记
  const cleaned = text.replace(/```json\n?/g, "").replace(/```\n?/g, "");
  return cleaned.trim();
}

/**
 * 调用 Gemini API 对单篇文章打分
 */
async function rankArticleWithRetry(
  client: GoogleGenerativeAI,
  article: Article
): Promise<{ score: number; ai_summary: string; ai_tags: string[] }> {
  const prompt = `你是一位中国烘焙食品行业分析师。请对以下新闻文章评分并生成摘要。
评分维度（总分0-100）：

行业相关性（30%）：与烘焙/食品制造/食品安全的直接相关度
决策价值（25%）：对企业采购、供应链、合规、市场决策的参考价值
时效性（20%）：信息的紧迫程度和新鲜度
信息深度（15%）：是否有具体数据、分析、而非泛泛而谈
独家性（10%）：是否为独家或首发信息

标题：${article.title}
摘要：${article.summary}
来源：${article.source_name}

请严格以JSON格式返回，不要添加其他文字：
{"score": 数字0-100, "summary": "中文摘要，150字以内，提炼核心信息和对烘焙食品行业的影响", "tags": ["从以下选择1-3个：烘焙行业,食品安全,原材料,政策法规,产品创新,渠道市场,供应链,行业展会"]}`;

  for (let attempt = 1; attempt <= MAX_RETRIES + 1; attempt++) {
    try {
      const model = client.getGenerativeModel({ model: "gemini-2.5-flash" });
      const result = await model.generateContent(prompt);
      const responseText = result.response.text();
      const cleanedJson = cleanJsonResponse(responseText);
      const parsed = JSON.parse(cleanedJson);

      return {
        score: Math.max(0, Math.min(100, parseInt(parsed.score) || 0)),
        ai_summary: (parsed.summary || article.summary).substring(0, 150),
        ai_tags: Array.isArray(parsed.tags) ? parsed.tags : [],
      };
    } catch (error) {
      if (attempt <= MAX_RETRIES) {
        console.error(
          `[AI] 第 ${attempt} 次尝试失败，${RETRY_DELAY_MS}ms 后重试: ${article.title.substring(0, 30)}`
        );
        await delay(RETRY_DELAY_MS);
      } else {
        console.error(
          `[AI] 打分失败 (重试 ${MAX_RETRIES} 次后放弃): ${article.title.substring(0, 30)}`
        );
        return {
          score: 0,
          ai_summary: article.summary,
          ai_tags: [],
        };
      }
    }
  }

  return {
    score: 0,
    ai_summary: article.summary,
    ai_tags: [],
  };
}

/**
 * 批量对文章进行 AI 打分
 */
export async function aiRankArticles(
  articles: Article[]
): Promise<ArticleWithRank[]> {
  if (!API_KEY) {
    console.log(
      `[AI] GEMINI_API_KEY 未设置，跳过 AI 打分，保留原始数据 (${articles.length} 篇)`
    );
    return articles.map((article) => ({
      ...article,
      score: 0,
      ai_summary: article.summary,
      ai_tags: [],
    }));
  }

  console.log(`\n[AI] 开始 Gemini API 打分 (${articles.length} 篇)...`);
  const client = new GoogleGenerativeAI(API_KEY);
  const result: ArticleWithRank[] = [];

  for (let i = 0; i < articles.length; i++) {
    const article = articles[i];
    const { score, ai_summary, ai_tags } = await rankArticleWithRetry(
      client,
      article
    );

    result.push({
      ...article,
      score,
      ai_summary,
      ai_tags,
    });

    const colorCode =
      score >= 70 ? "✓" : score >= 40 ? "~" : score > 0 ? "!" : "○";
    console.log(
      `[AI] ${colorCode} ${score.toString().padStart(3)} 分 | ${article.title.substring(0, 40)}`
    );

    // 避免触发 rate limit（最后一篇不需要延迟）
    if (i < articles.length - 1) {
      await delay(DELAY_MS);
    }
  }

  const highScore = result.filter((a) => a.score >= 70).length;
  const avgScore = (result.reduce((sum, a) => sum + a.score, 0) / result.length).toFixed(1);
  console.log(
    `[AI] 打分完成: ${result.length} 篇，平均分 ${avgScore}，高分 (≥70) ${highScore} 篇\n`
  );

  return result;
}
