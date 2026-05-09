import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { fetchAllFeeds } from "./fetch-feeds.js";
import { dedup } from "./utils/dedup.js";
import { filterJunkArticles } from "./filter.js";
import { categorizeArticles } from "./categorize.js";
import { loadSettings } from "./utils/config-loader.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  try {
    const startTime = Date.now();
    console.log(
      `\n[${new Date().toLocaleTimeString("zh-CN")}] ========== Daily Food News 开始运行 ==========`
    );

    // Step 1: 抓取所有源
    const allArticles = await fetchAllFeeds();

    if (allArticles.length === 0) {
      console.error(`\n[${new Date().toLocaleTimeString("zh-CN")}] 错误: 未获取到任何文章，停止运行`);
      process.exit(1);
    }

    // Step 2: 去重
    console.log(`\n[${new Date().toLocaleTimeString("zh-CN")}] Step 2: 开始去重...`);
    const dedupedArticles = dedup(allArticles);
    console.log(
      `  原始: ${allArticles.length} 篇 → 去重后: ${dedupedArticles.length} 篇 (去除 ${allArticles.length - dedupedArticles.length} 篇重复)`
    );

    // Step 3: 垃圾过滤
    console.log(`\n[${new Date().toLocaleTimeString("zh-CN")}] Step 3: 开始垃圾过滤...`);
    const filteredArticles = filterJunkArticles(dedupedArticles);
    console.log(
      `  去重后: ${dedupedArticles.length} 篇 → 过滤后: ${filteredArticles.length} 篇 (剔除 ${dedupedArticles.length - filteredArticles.length} 篇垃圾)`
    );

    // Step 4: 分类
    console.log(`\n[${new Date().toLocaleTimeString("zh-CN")}] Step 4: 开始分类...`);
    const categorizedArticles = categorizeArticles(filteredArticles);
    console.log(`  分类完成: ${categorizedArticles.length} 篇`);

    // Step 5: 按 settings 截断
    const settings = loadSettings();
    const displaySettings = settings.display;
    let finalArticles = categorizedArticles;

    if (displaySettings.max_items_per_category > 0) {
      console.log(
        `\n[${new Date().toLocaleTimeString("zh-CN")}] Step 5: 按每个分类截断到 ${displaySettings.max_items_per_category} 篇...`
      );

      const grouped: Record<string, typeof categorizedArticles> = {};
      for (const article of categorizedArticles) {
        const categoryId = article.primary_category;
        if (!grouped[categoryId]) {
          grouped[categoryId] = [];
        }
        grouped[categoryId].push(article);
      }

      const truncated: typeof categorizedArticles = [];
      for (const categoryId in grouped) {
        truncated.push(...grouped[categoryId].slice(0, displaySettings.max_items_per_category));
      }

      finalArticles = dedup(truncated);
      console.log(`  截断后: ${truncated.length} 篇，去重后: ${finalArticles.length} 篇`);
    }

    // Step 6: 写入 data/articles.json
    console.log(`\n[${new Date().toLocaleTimeString("zh-CN")}] Step 6: 写入数据...`);
    const dataDir = path.join(__dirname, "../data");
    const archiveDir = path.join(dataDir, "archive");

    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    if (!fs.existsSync(archiveDir)) {
      fs.mkdirSync(archiveDir, { recursive: true });
    }

    const articlesPath = path.join(dataDir, "articles.json");
    fs.writeFileSync(articlesPath, JSON.stringify(finalArticles, null, 2), "utf-8");
    console.log(`  ✓ 写入: ${articlesPath}`);

    // 同时复制到 site/src/data/ 供 Astro 访问
    const siteDataDir = path.join(__dirname, "../site/src/data");
    if (!fs.existsSync(siteDataDir)) {
      fs.mkdirSync(siteDataDir, { recursive: true });
    }
    const siteArticlesPath = path.join(siteDataDir, "articles.json");
    fs.writeFileSync(siteArticlesPath, JSON.stringify(finalArticles, null, 2), "utf-8");
    console.log(`  ✓ 写入: ${siteArticlesPath}`);

    // Step 6: 写入归档
    const today = new Date();
    const dateStr = today.toISOString().split("T")[0]; // YYYY-MM-DD
    const archivePath = path.join(archiveDir, `${dateStr}.json`);
    fs.writeFileSync(archivePath, JSON.stringify(finalArticles, null, 2), "utf-8");
    console.log(`  ✓ 写入: ${archivePath}`);

    // Step 7: 统计
    console.log(
      `\n[${new Date().toLocaleTimeString("zh-CN")}] ========== 执行完成 ==========`
    );
    console.log(`  总耗时: ${((Date.now() - startTime) / 1000).toFixed(2)} 秒`);
    console.log(`  抓取: ${allArticles.length} 篇`);
    console.log(`  去重: ${dedupedArticles.length} 篇`);
    console.log(`  过滤: ${filteredArticles.length} 篇`);
    console.log(`  最终: ${finalArticles.length} 篇`);

    // 计算分类统计
    const categoryCounts: Record<string, number> = {};
    for (const article of finalArticles) {
      for (const categoryId of article.category_ids) {
        categoryCounts[categoryId] = (categoryCounts[categoryId] || 0) + 1;
      }
    }

    console.log("\n  分类分布:");
    for (const [categoryId, count] of Object.entries(categoryCounts).sort((a, b) => b[1] - a[1])) {
      console.log(`    ${categoryId}: ${count} 篇`);
    }

    // 计算源分布
    const sourceCounts: Record<string, number> = {};
    for (const article of finalArticles) {
      sourceCounts[article.source_id] = (sourceCounts[article.source_id] || 0) + 1;
    }

    console.log("\n  源分布:");
    for (const [sourceId, count] of Object.entries(sourceCounts).sort((a, b) => b[1] - a[1])) {
      console.log(`    ${sourceId}: ${count} 篇`);
    }

    console.log(`\n[${new Date().toLocaleTimeString("zh-CN")}] ========== 准备退出 ==========\n`);

    process.exit(0);
  } catch (error) {
    console.error(`\n[ERROR] 致命错误:`, error);
    process.exit(1);
  }
}

main();
