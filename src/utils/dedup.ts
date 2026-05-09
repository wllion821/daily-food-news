export interface Article {
  source_id: string;
  source_name: string;
  tier: number;
  url: string;
  title: string;
  summary: string;
  published_at: string;
}

/**
 * 提取标题的前缀（前10个字符，去除标点和空格）
 */
function extractTitlePrefix(title: string): string {
  return title
    .replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '') // 去除标点
    .substring(0, 10); // 前10个字符
}

/**
 * 同源同模板去重：对同一个 source_id 的文章，如果标题前缀相同，只保留第一篇
 */
function dedupBySourceTemplate(articles: Article[]): Article[] {
  const groupedBySource: Record<string, Article[]> = {};
  for (const article of articles) {
    if (!groupedBySource[article.source_id]) {
      groupedBySource[article.source_id] = [];
    }
    groupedBySource[article.source_id].push(article);
  }

  const result: Article[] = [];
  for (const sourceArticles of Object.values(groupedBySource)) {
    const seenPrefixes = new Set<string>();
    for (const article of sourceArticles) {
      const prefix = extractTitlePrefix(article.title);
      if (!seenPrefixes.has(prefix)) {
        seenPrefixes.add(prefix);
        result.push(article);
      }
    }
  }

  return result;
}

/**
 * 计算两个字符串的 Jaccard 相似度
 * 用于标题相似度判断
 */
function jaccardSimilarity(s1: string, s2: string): number {
  const set1 = new Set(s1.split(""));
  const set2 = new Set(s2.split(""));

  const intersection = [...set1].filter((x) => set2.has(x)).length;
  const union = new Set([...set1, ...set2]).size;

  return union === 0 ? 0 : intersection / union;
}
export function dedup(articles: Article[]): Article[] {
  // 先进行同源同模板去重
  const templateDeduped = dedupBySourceTemplate(articles);

  const seenUrls = new Set<string>();
  const seenTitles = new Set<string>();
  const result: Article[] = [];

  for (const article of templateDeduped) {
    const urlNormalized = article.url
      .trim()
      .replace(/#.*$/, "")
      .replace(/\/+$/, "")
      .toLowerCase();
    const titleNormalized = article.title.trim().toLowerCase().replace(/\s+/g, " ");

    if (seenUrls.has(urlNormalized) || seenTitles.has(titleNormalized)) {
      continue;
    }

    let isDuplicate = false;
    for (const existing of result) {
      const existingTitle = existing.title.trim().toLowerCase().replace(/\s+/g, " ");
      if (existingTitle === titleNormalized) {
        isDuplicate = true;
        break;
      }
      const similarity = jaccardSimilarity(titleNormalized, existingTitle);
      if (similarity > 0.85) {
        isDuplicate = true;
        break;
      }
    }

    if (!isDuplicate) {
      seenUrls.add(urlNormalized);
      seenTitles.add(titleNormalized);
      result.push(article);
    }
  }

  return result;
}
