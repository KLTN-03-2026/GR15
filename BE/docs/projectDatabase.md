# Project Database

Tai lieu tong hop cac bang database cua du an backend Laravel trong thu muc `database/migrations`.

## 1. Bang nghiep vu chinh

### `nguoi_dungs`
- Muc dich: Luu thong tin tai khoan nguoi dung he thong.
- Khoa chinh: `id`
- Cot chinh:
  - `ho_ten`
  - `email` (unique)
  - `email_verified_at`
  - `mat_khau`
  - `so_dien_thoai`
  - `ngay_sinh`
  - `gioi_tinh` (`nam`, `nu`, `khac`)
  - `dia_chi`
  - `anh_dai_dien`
  - `vai_tro` (`0` ung_vien, `1` nha_tuyen_dung, `2` admin)
  - `trang_thai` (`1` active, `0` bi_khoa)
  - `created_at`, `updated_at`
- Ghi chu: truoc day co `remember_token` nhung da bi xoa bo.

### `ho_sos`
- Muc dich: Luu ho so/CV cua ung vien.
- Khoa chinh: `id`
- Khoa ngoai: `nguoi_dung_id -> nguoi_dungs.id`
- Cot chinh:
  - `nguoi_dung_id`
  - `tieu_de_ho_so`
  - `muc_tieu_nghe_nghiep`
  - `trinh_do`
  - `kinh_nghiem_nam`
  - `mo_ta_ban_than`
  - `file_cv`
  - `nguon_ho_so` (`upload`, `builder`, `hybrid`)
  - `mau_cv`
  - `che_do_mau_cv`
  - `vi_tri_ung_tuyen_muc_tieu`
  - `ten_nganh_nghe_muc_tieu`
  - `che_do_anh_cv`
  - `anh_cv`
  - `ky_nang_json`
  - `kinh_nghiem_json`
  - `hoc_van_json`
  - `du_an_json`
  - `chung_chi_json`
  - `trang_thai` (`1` cong_khai, `0` an)
  - `created_at`, `updated_at`, `deleted_at`

### `nganh_nghes`
- Muc dich: Danh muc nganh nghe.
- Khoa chinh: `id`
- Khoa ngoai: `danh_muc_cha_id -> nganh_nghes.id`
- Cot chinh:
  - `ten_nganh`
  - `slug` (unique)
  - `mo_ta`
  - `danh_muc_cha_id`
  - `icon`
  - `trang_thai`
  - `created_at`, `updated_at`

### `ky_nangs`
- Muc dich: Danh muc ky nang dung chung.
- Khoa chinh: `id`
- Cot chinh:
  - `ten_ky_nang`
  - `mo_ta`
  - `icon`
  - `created_at`, `updated_at`

### `nguoi_dung_ky_nangs`
- Muc dich: Bang lien ket giua nguoi dung va ky nang.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `ky_nang_id -> ky_nangs.id`
- Rang buoc:
  - unique (`nguoi_dung_id`, `ky_nang_id`)
- Cot chinh:
  - `nguoi_dung_id`
  - `ky_nang_id`
  - `muc_do`
  - `nam_kinh_nghiem`
  - `so_chung_chi`
  - `hinh_anh`
  - `nguon_du_lieu` (`manual`, `cv_parser`, `ai_inferred`)
  - `do_tin_cay`
  - `created_at`, `updated_at`

### `cong_tys`
- Muc dich: Luu thong tin cong ty tuyen dung.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `nganh_nghe_id -> nganh_nghes.id`
- Cot chinh:
  - `nguoi_dung_id`
  - `ten_cong_ty`
  - `ma_so_thue` (unique)
  - `mo_ta`
  - `dia_chi`
  - `dien_thoai`
  - `email`
  - `website`
  - `logo`
  - `nganh_nghe_id`
  - `quy_mo`
  - `trang_thai`
  - `created_at`, `updated_at`

### `cong_ty_nguoi_dungs`
- Muc dich: Quan ly thanh vien HR trong cong ty.
- Khoa chinh: `id`
- Khoa ngoai:
  - `cong_ty_id -> cong_tys.id`
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `duoc_tao_boi -> nguoi_dungs.id`
- Rang buoc:
  - unique (`cong_ty_id`, `nguoi_dung_id`)
  - unique (`nguoi_dung_id`)
- Cot chinh:
  - `cong_ty_id`
  - `nguoi_dung_id`
  - `vai_tro_noi_bo`
  - `duoc_tao_boi`
  - `created_at`, `updated_at`

### `tin_tuyen_dungs`
- Muc dich: Luu bai dang tin tuyen dung.
- Khoa chinh: `id`
- Khoa ngoai:
  - `cong_ty_id -> cong_tys.id`
  - `hr_phu_trach_id -> nguoi_dungs.id`
- Cot chinh:
  - `tieu_de`
  - `mo_ta_cong_viec`
  - `dia_diem_lam_viec`
  - `hinh_thuc_lam_viec`
  - `cap_bac`
  - `so_luong_tuyen`
  - `muc_luong`
  - `muc_luong_tu`
  - `muc_luong_den`
  - `don_vi_luong`
  - `kinh_nghiem_yeu_cau`
  - `trinh_do_yeu_cau`
  - `ngay_het_han` (datetime)
  - `luot_xem`
  - `cong_ty_id`
  - `hr_phu_trach_id`
  - `trang_thai`
  - `published_at`
  - `reactivated_at`
  - `created_at`, `updated_at`

### `chi_tiet_nganh_nghes`
- Muc dich: Bang lien ket giua tin tuyen dung va nganh nghe.
- Khoa chinh: `id`
- Khoa ngoai:
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
  - `nganh_nghe_id -> nganh_nghes.id`
- Rang buoc:
  - unique (`tin_tuyen_dung_id`, `nganh_nghe_id`)
- Cot chinh:
  - `tin_tuyen_dung_id`
  - `nganh_nghe_id`
  - `created_at`, `updated_at`

### `tin_tuyen_dung_ky_nangs`
- Muc dich: Chuan hoa cac ky nang yeu cau cua tin tuyen dung.
- Khoa chinh: `id`
- Khoa ngoai:
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
  - `ky_nang_id -> ky_nangs.id`
- Rang buoc:
  - unique (`tin_tuyen_dung_id`, `ky_nang_id`)
- Cot chinh:
  - `tin_tuyen_dung_id`
  - `ky_nang_id`
  - `muc_do_yeu_cau`
  - `bat_buoc`
  - `trong_so`
  - `nguon_du_lieu` (`manual`, `jd_parser`, `ai_inferred`)
  - `do_tin_cay`
  - `created_at`, `updated_at`

### `luu_tins`
- Muc dich: Luu danh sach tin duoc nguoi dung quan tam.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
- Rang buoc:
  - unique (`nguoi_dung_id`, `tin_tuyen_dung_id`)
- Cot chinh:
  - `nguoi_dung_id`
  - `tin_tuyen_dung_id`
  - `created_at`, `updated_at`

### `theo_doi_cong_tys`
- Muc dich: Luu danh sach cong ty duoc nguoi dung theo doi.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `cong_ty_id -> cong_tys.id`
- Rang buoc:
  - unique (`nguoi_dung_id`, `cong_ty_id`)
- Cot chinh:
  - `nguoi_dung_id`
  - `cong_ty_id`
  - `created_at`, `updated_at`

### `ung_tuyens`
- Muc dich: Luu ho so ung tuyen vao tung tin.
- Khoa chinh: `id`
- Khoa ngoai:
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
  - `ho_so_id -> ho_sos.id`
  - `hr_phu_trach_id -> nguoi_dungs.id`
- Rang buoc:
  - unique (`tin_tuyen_dung_id`, `ho_so_id`)
- Cot chinh:
  - `tin_tuyen_dung_id`
  - `ho_so_id`
  - `hr_phu_trach_id`
  - `trang_thai`
  - `da_rut_don`
  - `thoi_gian_rut_don`
  - `thu_xin_viec`
  - `thu_xin_viec_ai`
  - `ngay_hen_phong_van`
  - `vong_phong_van_hien_tai`
  - `trang_thai_tham_gia_phong_van`
  - `thoi_gian_phan_hoi_phong_van`
  - `hinh_thuc_phong_van`
  - `nguoi_phong_van`
  - `link_phong_van`
  - `ket_qua_phong_van`
  - `rubric_danh_gia_phong_van`
  - `ghi_chu`
  - `lich_su_xu_ly`
  - `thoi_gian_gui_nhac_lich`
  - `thoi_gian_gui_offer`
  - `thoi_gian_phan_hoi_offer`
  - `ghi_chu_offer`
  - `link_offer`
  - `thoi_gian_ung_tuyen`
  - `created_at`, `updated_at`
- Ghi chu trang thai:
  - `0` cho_duyet
  - `1` da_xem
  - `2` da_hen_phong_van
  - `3` qua_phong_van
  - `4` trung_tuyen
  - `5` tu_choi

### `ket_qua_matchings`
- Muc dich: Luu ket qua matching giua ho so va tin tuyen dung.
- Khoa chinh: `id`
- Khoa ngoai:
  - `ho_so_id -> ho_sos.id`
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
- Rang buoc:
  - unique (`ho_so_id`, `tin_tuyen_dung_id`, `model_version`)
- Cot chinh:
  - `ho_so_id`
  - `tin_tuyen_dung_id`
  - `diem_phu_hop`
  - `diem_ky_nang`
  - `diem_kinh_nghiem`
  - `diem_hoc_van`
  - `chi_tiet_diem`
  - `matched_skills_json`
  - `missing_skills_json`
  - `explanation`
  - `danh_sach_ky_nang_thieu`
  - `model_version`
  - `thoi_gian_match`
  - `created_at`, `updated_at`

### `tu_van_nghe_nghieps`
- Muc dich: Luu ket qua AI tu van nghe nghiep.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `ho_so_id -> ho_sos.id`
- Cot chinh:
  - `nguoi_dung_id`
  - `ho_so_id`
  - `nghe_de_xuat`
  - `muc_do_phu_hop`
  - `goi_y_ky_nang_bo_sung` (json)
  - `bao_cao_chi_tiet`
  - `model_version`
  - `created_at`, `updated_at`

## 2. Bang AI va xu ly du lieu

### `ho_so_parsings`
- Muc dich: Ket qua parser CV.
- Khoa chinh: `id`
- Khoa ngoai: `ho_so_id -> ho_sos.id`
- Rang buoc:
  - unique (`ho_so_id`)
- Cot chinh:
  - `ho_so_id`
  - `raw_text`
  - `parsed_name`
  - `parsed_email`
  - `parsed_phone`
  - `parsed_skills_json`
  - `parsed_experience_json`
  - `parsed_education_json`
  - `parse_status`
  - `parser_version`
  - `confidence_score`
  - `error_message`
  - `created_at`, `updated_at`

### `tin_tuyen_dung_parsings`
- Muc dich: Ket qua parser mo ta cong viec/JD.
- Khoa chinh: `id`
- Khoa ngoai: `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
- Rang buoc:
  - unique (`tin_tuyen_dung_id`)
- Cot chinh:
  - `tin_tuyen_dung_id`
  - `raw_text`
  - `parsed_skills_json`
  - `parsed_requirements_json`
  - `parsed_benefits_json`
  - `parsed_salary_json`
  - `parsed_location_json`
  - `parse_status`
  - `parser_version`
  - `confidence_score`
  - `error_message`
  - `created_at`, `updated_at`

### `vector_embeddings`
- Muc dich: Luu vector embedding phuc vu tim kiem ngu nghia/semantic search.
- Khoa chinh: `id`
- Rang buoc:
  - unique (`entity_type`, `entity_id`, `chunk_index`)
- Cot chinh:
  - `entity_type` (`ho_so`, `tin_tuyen_dung`, `ai_chat_message`, `tu_van_nghe_nghiep`)
  - `entity_id`
  - `chunk_index`
  - `text_content`
  - `embedding_vector`
  - `model_name`
  - `embedding_hash`
  - `metadata_json`
  - `created_at`, `updated_at`

### `ai_chat_sessions`
- Muc dich: Phien chat AI voi nguoi dung.
- Khoa chinh: `id`
- Khoa ngoai:
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `related_ho_so_id -> ho_sos.id`
  - `related_tin_tuyen_dung_id -> tin_tuyen_dungs.id`
- Cot chinh:
  - `nguoi_dung_id`
  - `session_type` (`career_consultant`, `mock_interview`)
  - `related_ho_so_id`
  - `related_tin_tuyen_dung_id`
  - `status`
  - `title`
  - `summary`
  - `metadata`
  - `created_at`, `updated_at`

### `ai_chat_messages`
- Muc dich: Tin nhan thuoc tung phien chat AI.
- Khoa chinh: `id`
- Khoa ngoai: `session_id -> ai_chat_sessions.id`
- Cot chinh:
  - `session_id`
  - `role` (`system`, `user`, `assistant`, `tool`)
  - `content`
  - `metadata`
  - `created_at`

### `ai_interview_reports`
- Muc dich: Bao cao danh gia mock interview do AI sinh ra.
- Khoa chinh: `id`
- Khoa ngoai:
  - `session_id -> ai_chat_sessions.id`
  - `nguoi_dung_id -> nguoi_dungs.id`
  - `tin_tuyen_dung_id -> tin_tuyen_dungs.id`
- Rang buoc:
  - unique (`session_id`)
- Cot chinh:
  - `session_id`
  - `nguoi_dung_id`
  - `tin_tuyen_dung_id`
  - `tong_diem`
  - `diem_ky_thuat`
  - `diem_giao_tiep`
  - `diem_phu_hop_jd`
  - `diem_manh`
  - `diem_yeu`
  - `de_xuat_cai_thien`
  - `metadata`
  - `created_at`, `updated_at`

### `market_stats_daily`
- Muc dich: Thong ke thi truong viec lam theo ngay.
- Khoa chinh: `id`
- Khoa ngoai: `nganh_nghe_id -> nganh_nghes.id`
- Rang buoc:
  - unique (`stat_date`, `nganh_nghe_id`)
- Cot chinh:
  - `stat_date`
  - `nganh_nghe_id`
  - `avg_salary`
  - `median_salary`
  - `demand_count`
  - `top_skills`
  - `created_at`

## 3. Bang he thong mac dinh cua Laravel

### `users`
- Bang mac dinh scaffold cua Laravel.
- Cot chinh: `id`, `name`, `email`, `email_verified_at`, `password`, `remember_token`, `created_at`, `updated_at`
- Ghi chu: du an dang dung bang `nguoi_dungs` cho nghiep vu chinh, nen bang nay co the chi la phan scaffold con lai.

### `password_reset_tokens`
- Cot chinh: `email`, `token`, `created_at`

### `sessions`
- Cot chinh: `id`, `user_id`, `ip_address`, `user_agent`, `payload`, `last_activity`

### `personal_access_tokens`
- Cot chinh: `id`, `tokenable_type`, `tokenable_id`, `name`, `token`, `abilities`, `last_used_at`, `expires_at`, `created_at`, `updated_at`

### `cache`
- Cot chinh: `key`, `value`, `expiration`

### `cache_locks`
- Cot chinh: `key`, `owner`, `expiration`

### `jobs`
- Cot chinh: `id`, `queue`, `payload`, `attempts`, `reserved_at`, `available_at`, `created_at`

### `job_batches`
- Cot chinh: `id`, `name`, `total_jobs`, `pending_jobs`, `failed_jobs`, `failed_job_ids`, `options`, `cancelled_at`, `created_at`, `finished_at`

### `failed_jobs`
- Cot chinh: `id`, `uuid`, `connection`, `queue`, `payload`, `exception`, `failed_at`

## 4. Tong hop nhanh so luong bang

- Bang nghiep vu chinh: 13 bang
- Bang AI va xu ly du lieu: 7 bang
- Bang he thong Laravel: 9 bang
- Tong cong: 29 bang

## 5. Quan he chinh trong he thong

- `nguoi_dungs` 1-n `ho_sos`
- `nguoi_dungs` n-n `ky_nangs` qua `nguoi_dung_ky_nangs`
- `nguoi_dungs` 1-1 hoac 1-n voi `cong_tys`/`cong_ty_nguoi_dungs` tuy theo vai tro
- `cong_tys` 1-n `tin_tuyen_dungs`
- `tin_tuyen_dungs` n-n `nganh_nghes` qua `chi_tiet_nganh_nghes`
- `tin_tuyen_dungs` 1-n `ung_tuyens`
- `ho_sos` 1-n `ung_tuyens`
- `ho_sos` va `tin_tuyen_dungs` 1-n `ket_qua_matchings`
- `nguoi_dungs` 1-n `tu_van_nghe_nghieps`
- `ai_chat_sessions` 1-n `ai_chat_messages`
- `ai_chat_sessions` 1-1 `ai_interview_reports`

