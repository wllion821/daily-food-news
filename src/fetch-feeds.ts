import Parser from "rss-parser";
import * as cheerio from "cheerio";
import { loadFeeds, loadSettings } from "./utils/config-loader.js";
import { Article } from "./utils/dedup.js";

const parser = new Parser();

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 抓取 RSS 源
 */
async function fetchRSS(sourceId: string, sourceUrl: string): Promise<Article[]> {
  const settings = loadSettings();
  const timeout = settings.fetch.timeout_seconds * 1000;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const feed = await parser.parseURL(sourceUrl);
    clearTimeout(timeoutId);

    const articles: Article[] = (feed.items || []).slice(0, settings.fetch.max_articles_per_source).map((item) => ({
      source_id: sourceId,
      source_name: feed.title || sourceId,
      tier: 1,
      url: item.link || "",
      title: item.title || "",
      summary: item.content || item.summary || "",
      published_at: item.pubDate || new Date().toISOString(),
    }));

    return articles;
  } catch (error) {
    console.error(`[RSS] ${sourceId} 抓取失败:`, error);
    return [];
  }
}

/**
 * 抓取网页并提取文章链接
 */
async function fetchWebpage(url: string): Promise<string> {
  const settings = loadSettings();
  const timeout = settings.fetch.timeout_seconds * 1000;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(url, {
      headers: {
        "User-Agent": settings.fetch.user_agent,
      },
      signal: controller.signal as any,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.text();
  } catch (error) {
    console.error(`[SCRAPE] ${url} 获取失败:`, error);
    return "";
  }
}

/**
 * 从网页内容中提取文章链接
 */
function extractArticleLinks(
  html: string,
  baseUrl: string,
  pattern: string
): string[] {
  const $ = cheerio.load(html);
  const regex = new RegExp(pattern);
  const links = new Set<string>();

  $("a").each((_, element) => {
    const href = $(element).attr("href") || "";
    if (regex.test(href)) {
      try {
        const fullUrl = new URL(href, baseUrl).toString();
        links.add(fullUrl);
      } catch {
        // 忽略无效 URL
      }
    }
  });

  return Array.from(links);
}

/**
 * 抓取单篇文章的标题和摘要
 */
async function fetchArticleDetails(articleUrl: string): Promise<{ title: string; summary: string }> {
  const html = await fetchWebpage(articleUrl);
  if (!html) {
    return { title: "", summary: "" };
  }

  const $ = cheerio.load(html);
  const title = $("h1, .title, [class*='title']").first().text().trim() || new URL(articleUrl).pathname;
  const summary = $("p, [class*='summary'], [class*='content']")
    .first()
    .text()
    .trim()
    .slice(0, 300);

  return { title, summary };
}

/**
 * 抓取 Scrape 类型的源
 */
async function fetchScrape(
  sourceId: string,
  sourceName: string,
  sourceUrl: string,
  articlePattern: string
): Promise<Article[]> {
  const settings = loadSettings();

  try {
    // 第一步：获取首页并提取文章链接
    const homepage = await fetchWebpage(sourceUrl);
    if (!homepage) {
      return [];
    }

    const articleLinks = extractArticleLinks(homepage, sourceUrl, articlePattern).slice(
      0,
      settings.fetch.max_articles_per_source
    );

    const articles: Article[] = [];

    // 第二步：并发抓取各篇文章详情
    for (const link of articleLinks) {
      await delay(settings.fetch.delay_between_requests * 1000);

      const { title, summary } = await fetchArticleDetails(link);

      if (title) {
        articles.push({
          source_id: sourceId,
          source_name: sourceName,
          tier: 1,
          url: link,
          title,
          summary,
          published_at: new Date().toISOString(),
        });
      }
    }

    return articles;
  } catch (error) {
    console.error(`[SCRAPE] ${sourceId} 抓取失败:`, error);
    return [];
  }
}

/**
 * 主抓取函数：并发抓取所有源
 */
export async function fetchAllFeeds(): Promise<Article[]> {
  const feeds = loadFeeds();
  const settings = loadSettings();
  const enabledFeeds = feeds.filter((f) => f.enabled);

  console.log(
    `[${new Date().toLocaleTimeString("zh-CN")}] Step 1: 开始抓取 ${enabledFeeds.length} 个源...`
  );

  const allArticles: Article[] = [];

  for (const feed of enabledFeeds) {
    let articles: Article[] = [];

    try {
      if (feed.type === "rss") {
        articles = await fetchRSS(feed.id, feed.url);
      } else if (feed.type === "scrape") {
        articles = await fetchScrape(feed.id, feed.name, feed.url, feed.article_pattern || "");
      }

      if (articles.length > 0) {
        console.log(`  ✓ ${feed.name}: ${articles.length} 篇`);
        allArticles.push(...articles);
      } else {
        console.log(`  ✗ ${feed.name}: 无结果`);
      }
    } catch (error) {
      console.error(`  ✗ ${feed.name}:`, error);
    }

    // 请求之间延迟
    await delay(settings.fetch.delay_between_requests * 1000);
  }

  console.log(`  总共: ${allArticles.length} 篇文章`);
  return allArticles;
}
