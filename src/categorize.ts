import { Article } from "./utils/dedup.js";
import { loadCategories, loadKeywords } from "./utils/config-loader.js";

export interface ArticleWithCategory extends Article {
  category_ids: string[];
  primary_category: string;
  signals: string[];
}

/**
 * 根据关键词匹配对文章进行分类
 * 返回分类 ID 列表、主要分类和信号列表
 */
export function categorizeArticle(article: Article): {
  category_ids: string[];
  primary_category: string;
  signals: string[];
} {
  const categories = loadCategories();
  const keywords = loadKeywords();

  const text = `${article.title} ${article.summary}`.toLowerCase();
  const matchedCategories = new Set<string>();
  const matchedSignals = new Set<string>();
  const categoryScores: Record<string, number> = {};

  // 检查每个分类
  for (const category of categories) {
    let score = 0;

    // 检查分类关键词
    for (const kw of category.match_keywords) {
      if (text.includes(kw.toLowerCase())) {
        score++;
      }
    }

    if (score > 0) {
      matchedCategories.add(category.id);
      categoryScores[category.id] = score;
    }

    // 检查信号关键词
    for (const signal of category.match_signals) {
      const signalKeywords = keywords.signals[signal] || [];
      for (const kw of signalKeywords) {
        if (text.includes(kw.toLowerCase())) {
          matchedSignals.add(signal);
          break;
        }
      }
    }
  }

  // 如果没有匹配任何分类，归入 "other"
  if (matchedCategories.size === 0) {
    matchedCategories.add("other");
    categoryScores["other"] = 0;
  }

  // 选择主要分类：最高分数，如果平分按categories.json顺序取第一个
  let primaryCategory = "other";
  let maxScore = -1;
  for (const category of categories) {
    const score = categoryScores[category.id] || 0;
    if (score > maxScore) {
      maxScore = score;
      primaryCategory = category.id;
    }
  }
  // 如果other有匹配，检查是否比当前高
  if (categoryScores["other"] !== undefined && categoryScores["other"] > maxScore) {
    primaryCategory = "other";
  }

  return {
    category_ids: Array.from(matchedCategories),
    primary_category: primaryCategory,
    signals: Array.from(matchedSignals),
  };
}

/**
 * 批量对文章进行分类
 */
export function categorizeArticles(articles: Article[]): ArticleWithCategory[] {
  return articles.map((article) => {
    const { category_ids, primary_category, signals } = categorizeArticle(article);
    return {
      ...article,
      category_ids,
      primary_category,
      signals,
    };
  });
}

/**
 * 按主要分类分组
 */
export function groupByCategory(articles: ArticleWithCategory[]): Record<string, ArticleWithCategory[]> {
  const grouped: Record<string, ArticleWithCategory[]> = {};

  for (const article of articles) {
    const categoryId = article.primary_category;
    if (!grouped[categoryId]) {
      grouped[categoryId] = [];
    }
    grouped[categoryId].push(article);
  }

  return grouped;
}
