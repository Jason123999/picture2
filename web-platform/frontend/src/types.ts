export type Tenant = {
  id: number;
  name: string;
  slug: string;
  custom_domain?: string | null;
  contact_email?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ImageAsset = {
  id: number;
  tenant_id: number;
  uploaded_by_id: number;
  original_path: string;
  processed_path?: string | null;
  thumbnail_path?: string | null;
  status: string;
  meta_json?: string | null;
  created_at: string;
  updated_at: string;
};

export type Task = {
  id: number;
  tenant_id: number;
  image_asset_id: number;
  status: "pending" | "processing" | "completed" | "failed";
  error_message?: string | null;
  result_path?: string | null;
  created_at: string;
  updated_at: string;
};

export type UploadResponse = {
  storage_key: string;
  url: string;
  local_path: string;
  filename: string;
};
