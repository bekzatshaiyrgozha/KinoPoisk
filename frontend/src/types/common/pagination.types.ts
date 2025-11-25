export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface PaginationMeta {
  current_page: number;
  total_pages: number;
  total_count: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}
