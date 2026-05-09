import { Article } from "./utils/dedup.js";
import { loadFilters } from "./utils/config-loader.js";

export function filterJunkArticles(articles: Article[]): Article[] {
  const filters = loadFilters();
  const filtered: Article[] = [];

  for (const article of articles) {
    let reason = "";

    // 1. 标题长度检查
    if (article.title.length < filters.min_title_length) {
      reason = `标题长度 ${article.title.length} < ${filters.min_title_length}`;
    }

    // 2. 标题最大长度检查
    if (!reason && article.title.length > filters.max_title_length) {
      reason = `标题长度 ${article.title.length} > ${filters.max_title_length}`;
    }

    // 3. 摘要长度检查
    if (!reason && article.summary.length < filters.min_summary_length) {
      reason = `摘要长度 ${article.summary.length} < ${filters.min_summary_length}`;
    }

    // 4. 标题必须包含中文字符
    if (!reason && !/[\u4e00-\u9fa5]/.test(article.title)) {
      reason = `标题不包含中文字符: ${article.title}`;
    }

    // 5. 标题黑名单关键词
    if (!reason) {
      for (const keyword of filters.title_blacklist) {
        if (article.title.toLowerCase().includes(keyword.toLowerCase())) {
          reason = `标题包含黑名单关键词: ${keyword}`;
          break;
        }
      }
    }

    // 6. 标题黑名单正则
    if (!reason) {
      for (const pattern of filters.title_patterns_blacklist) {
        const regex = new RegExp(pattern, "i");
        if (regex.test(article.title)) {
          reason = `标题匹配黑名单正则: ${pattern}`;
          break;
        }
      }
    }

    // 7. 摘要黑名单关键词
    if (!reason) {
      for (const keyword of filters.summary_blacklist) {
        if (article.summary.toLowerCase().includes(keyword.toLowerCase())) {
          reason = `摘要包含黑名单关键词: ${keyword}`;
          break;
        }
      }
    }

    // 8. 通用来源的食品关键词要求
    if (!reason && filters.general_sources.includes(article.source_id)) {
      const text = `${article.title} ${article.summary}`.toLowerCase();
      let hasFoodKeyword = false;
      for (const keyword of filters.general_source_require_food_keywords) {
        if (text.includes(keyword.toLowerCase())) {
          hasFoodKeyword = true;
          break;
        }
      }
      if (!hasFoodKeyword) {
        reason = `通用来源 ${article.source_id} 缺少食品关键词`;
      }
    }

    if (reason) {
      console.log(`[FILTER] 剔除: ${reason} | ${article.title}`);
    } else {
      filtered.push(article);
    }
  }

  return filtered;
}