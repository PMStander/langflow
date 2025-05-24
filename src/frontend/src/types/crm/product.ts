import { BaseEntity } from './common';

export interface ProductDimensions {
  length: string;
  width: string;
  height: string;
}

export interface ProductDownload {
  id: string;
  name: string;
  file: string;
}

export interface ProductImage {
  id: string;
  src: string;
  name: string;
  alt: string;
}

export interface Product extends BaseEntity {
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  sku?: string;
  price: number;
  regular_price: number;
  sale_price?: number;
  on_sale: boolean;
  status: string;
  featured: boolean;
  catalog_visibility: string;
  tax_status: string;
  tax_class?: string;
  manage_stock: boolean;
  stock_quantity?: number;
  stock_status: string;
  backorders: string;
  backorders_allowed: boolean;
  backordered: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  virtual: boolean;
  downloadable: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  sold_individually: boolean;
  external_url?: string;
  button_text?: string;
  menu_order: number;
  purchasable: boolean;
  images?: ProductImage[];
  categories?: ProductCategory[];
  attributes?: ProductAttribute[];
  variations?: ProductVariation[];
  meta_data?: ProductMeta[];
}

export interface ProductCreate {
  name: string;
  slug: string;
  description?: string;
  short_description?: string;
  sku?: string;
  price: number;
  regular_price: number;
  sale_price?: number;
  on_sale?: boolean;
  status?: string;
  featured?: boolean;
  catalog_visibility?: string;
  tax_status?: string;
  tax_class?: string;
  manage_stock?: boolean;
  stock_quantity?: number;
  stock_status?: string;
  backorders?: string;
  backorders_allowed?: boolean;
  backordered?: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  virtual?: boolean;
  downloadable?: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  sold_individually?: boolean;
  external_url?: string;
  button_text?: string;
  menu_order?: number;
  purchasable?: boolean;
  images?: ProductImage[];
  workspace_id: string;
  category_ids?: string[];
  attribute_ids?: string[];
}

export interface ProductUpdate {
  name?: string;
  slug?: string;
  description?: string;
  short_description?: string;
  sku?: string;
  price?: number;
  regular_price?: number;
  sale_price?: number;
  on_sale?: boolean;
  status?: string;
  featured?: boolean;
  catalog_visibility?: string;
  tax_status?: string;
  tax_class?: string;
  manage_stock?: boolean;
  stock_quantity?: number;
  stock_status?: string;
  backorders?: string;
  backorders_allowed?: boolean;
  backordered?: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  virtual?: boolean;
  downloadable?: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  sold_individually?: boolean;
  external_url?: string;
  button_text?: string;
  menu_order?: number;
  purchasable?: boolean;
  images?: ProductImage[];
  category_ids?: string[];
  attribute_ids?: string[];
}

export interface ProductCategory extends BaseEntity {
  name: string;
  slug: string;
  description?: string;
  parent_id?: string;
  display: string;
  parent?: ProductCategory;
  children?: ProductCategory[];
  products?: Product[];
}

export interface ProductCategoryCreate {
  name: string;
  slug: string;
  description?: string;
  parent_id?: string;
  display?: string;
  workspace_id: string;
}

export interface ProductCategoryUpdate {
  name?: string;
  slug?: string;
  description?: string;
  parent_id?: string;
  display?: string;
}

export interface ProductAttribute extends BaseEntity {
  name: string;
  slug: string;
  type: string;
  order_by: string;
  has_archives: boolean;
  terms?: ProductAttributeTerm[];
  products?: Product[];
}

export interface ProductAttributeCreate {
  name: string;
  slug: string;
  type?: string;
  order_by?: string;
  has_archives?: boolean;
  workspace_id: string;
}

export interface ProductAttributeUpdate {
  name?: string;
  slug?: string;
  type?: string;
  order_by?: string;
  has_archives?: boolean;
}

export interface ProductAttributeTerm extends BaseEntity {
  name: string;
  slug: string;
  description?: string;
  menu_order: number;
  attribute_id: string;
  attribute?: ProductAttribute;
}

export interface ProductAttributeTermCreate {
  name: string;
  slug: string;
  description?: string;
  menu_order?: number;
  attribute_id: string;
}

export interface ProductAttributeTermUpdate {
  name?: string;
  slug?: string;
  description?: string;
  menu_order?: number;
}

export interface ProductVariation extends BaseEntity {
  description?: string;
  sku?: string;
  price: number;
  regular_price: number;
  sale_price?: number;
  on_sale: boolean;
  status: string;
  virtual: boolean;
  downloadable: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  tax_status: string;
  tax_class?: string;
  manage_stock: boolean;
  stock_quantity?: number;
  stock_status: string;
  backorders: string;
  backorders_allowed: boolean;
  backordered: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  menu_order: number;
  attributes?: Record<string, any>;
  image?: ProductImage;
  product_id: string;
  product?: Product;
}

export interface ProductVariationCreate {
  description?: string;
  sku?: string;
  price: number;
  regular_price: number;
  sale_price?: number;
  on_sale?: boolean;
  status?: string;
  virtual?: boolean;
  downloadable?: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  tax_status?: string;
  tax_class?: string;
  manage_stock?: boolean;
  stock_quantity?: number;
  stock_status?: string;
  backorders?: string;
  backorders_allowed?: boolean;
  backordered?: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  menu_order?: number;
  attributes?: Record<string, any>;
  image?: ProductImage;
  product_id: string;
}

export interface ProductVariationUpdate {
  description?: string;
  sku?: string;
  price?: number;
  regular_price?: number;
  sale_price?: number;
  on_sale?: boolean;
  status?: string;
  virtual?: boolean;
  downloadable?: boolean;
  downloads?: ProductDownload[];
  download_limit?: number;
  download_expiry?: number;
  tax_status?: string;
  tax_class?: string;
  manage_stock?: boolean;
  stock_quantity?: number;
  stock_status?: string;
  backorders?: string;
  backorders_allowed?: boolean;
  backordered?: boolean;
  weight?: string;
  dimensions?: ProductDimensions;
  shipping_class?: string;
  shipping_class_id?: number;
  menu_order?: number;
  attributes?: Record<string, any>;
  image?: ProductImage;
}

export interface ProductMeta extends BaseEntity {
  key: string;
  value: any;
  product_id: string;
  product?: Product;
}

export interface ProductReview extends BaseEntity {
  rating: number;
  title?: string;
  content?: string;
  status: string;
  reviewer_name?: string;
  reviewer_email?: string;
  verified_purchase: boolean;
  product_id: string;
  created_by?: string;
  product?: Product;
}

export interface ProductMetaCreate {
  key: string;
  value: any;
  product_id: string;
}

export interface ProductMetaUpdate {
  key?: string;
  value?: any;
}

export interface ProductReviewCreate {
  rating: number;
  title?: string;
  content?: string;
  reviewer_name?: string;
  reviewer_email?: string;
  verified_purchase?: boolean;
  product_id: string;
}

export interface ProductReviewUpdate {
  rating?: number;
  title?: string;
  content?: string;
  status?: string;
  reviewer_name?: string;
  reviewer_email?: string;
  verified_purchase?: boolean;
}
