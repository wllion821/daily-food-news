import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const configDir = path.join(__dirname, "../../config");

interface Feed {
  id: string;
  name: string;
  url: string;
  type: "rss" | "scrape";
  tier: number;
  article_pattern?: string;
  enabled: boolean;
}

interface FeedsConfig {
  sources: Feed[];
}

interface Category {
  id: string;
  name: string;
  description: string;
  match_signals: string[];
  match_keywords: string[];
}

interface CategoriesConfig {
  categories: Category[];
}

interface Keywords {
  brands: Record<string, string[]>;
  signals: Record<string, string[]>;
}

interface FetchSettings {
  timeout_seconds: number;
  delay_between_requests: number;
  max_articles_per_source: number;
  user_agent: string;
}

interface FilterSettings {
  min_title_length: number;
  min_signal_score: number;
  require_brand_match: boolean;
  fallback_top_n: number;
}

interface DisplaySettings {
  max_items_per_category: number;
  title_max_length: number;
  summary_max_length: number;
  site_title: string;
  site_subtitle: string;
  footer_text: string;
}

interface ScheduleSettings {
  cron: string;
  timezone: string;
}

interface Settings {
  fetch: FetchSettings;
  filter: FilterSettings;
  display: DisplaySettings;
  schedule: ScheduleSettings;
}

interface Filters {
  title_blacklist: string[];
  title_patterns_blacklist: string[];
  summary_blacklist: string[];
  min_title_length: number;
  min_summary_length: number;
  max_signals_required_if_general_source: number;
  general_sources: string[];
  general_source_require_food_keywords: string[];
}

export function loadFeeds(): Feed[] {
  const feedsPath = path.join(configDir, "feeds.json");
  const content = fs.readFileSync(feedsPath, "utf-8");
  const config: FeedsConfig = JSON.parse(content);
  return config.sources;
}

export function loadKeywords(): Keywords {
  const keywordsPath = path.join(configDir, "keywords.json");
  const content = fs.readFileSync(keywordsPath, "utf-8");
  return JSON.parse(content);
}

export function loadCategories(): Category[] {
  const categoriesPath = path.join(configDir, "categories.json");
  const content = fs.readFileSync(categoriesPath, "utf-8");
  const config: CategoriesConfig = JSON.parse(content);
  return config.categories;
}

export function loadSettings(): Settings {
  const settingsPath = path.join(configDir, "settings.json");
  const content = fs.readFileSync(settingsPath, "utf-8");
  return JSON.parse(content);
}

export function loadFilters(): Filters {
  const filtersPath = path.join(configDir, "filters.json");
  const content = fs.readFileSync(filtersPath, "utf-8");
  return JSON.parse(content);
}
