# Tong hop cac tinh nang AI trong he thong

Tai lieu nay tong hop y nghia, tinh nang, ket qua, ly do thiet ke va huong toi uu cho cac tinh nang AI hien tai cua he thong tuyen dung.

## 1. Kien truc tong quan

He thong AI hien tai gom 3 lop chinh:

1. Lop xu ly du lieu nen:
   - Parse CV.
   - Parse JD.
   - Semantic Search.
   - Matching CV - JD.

2. Lop AI cho ung vien:
   - Matched Jobs.
   - Career Report.
   - Chatbot AI tu van nghe nghiep.
   - Mock Interview.
   - Cover Letter AI.
   - CV Tailoring.
   - CV Builder AI Writing.

3. Lop AI cho nha tuyen dung:
   - AI Shortlist.
   - AI Compare ung vien.
   - Interview Copilot generate.
   - Interview Copilot evaluate.

Laravel backend goi FastAPI AI service thong qua `App\Services\Ai\AiClientService`.

AI service hien dang dang ky cac router:

- `/parse/cv`
- `/parse/jd`
- `/match/cv-jd`
- `/generate/*`
- `/search/semantic/jobs`
- `/chat/career-consultant`
- `/interview/mock/*`
- `/interview/copilot/*`

## 2. Bang tong hop nhanh

| Tinh nang | Nguoi dung | Y nghia | Ket qua chinh |
|---|---|---|---|
| Parse CV | Ung vien / He thong | Trich xuat noi dung CV thanh du lieu co cau truc | raw text, ten, email, phone, skills, experience, education |
| Parse JD | He thong / Nha tuyen dung | Trich xuat noi dung tin tuyen dung | skills, requirements, benefits, salary, location |
| Semantic Search | Khach / Ung vien | Tim viec bang ngon ngu tu nhien | danh sach job lien quan, diem semantic, ly do khop |
| Matched Jobs | Ung vien | So khop CV voi tin tuyen dung | diem phu hop, diem ky nang, diem kinh nghiem, skill khop/thieu |
| Career Report | Ung vien | Tu van huong nghe nghiep | nghe de xuat, muc do phu hop, ky nang can bo sung |
| Chatbot AI | Ung vien | Tu van nghe nghiep theo hoi dap | cau tra loi theo context CV/report/job |
| Mock Interview | Ung vien | Luyen phong van mo phong | cau hoi, cham cau tra loi, bao cao tong ket |
| Cover Letter AI | Ung vien | Sinh thu xin viec theo CV va JD | thu xin viec ca nhan hoa |
| CV Tailoring | Ung vien | Toi uu CV theo mot JD cu the | CV goi y, keyword khop, skill gaps |
| CV Builder AI Writing | Ung vien | Goi y viet tung phan CV | summary, kinh nghiem, muc tieu, ky nang |
| AI Shortlist | Nha tuyen dung | Loc ung vien phu hop voi tin tuyen dung | danh sach ung vien, diem, giai thich AI |
| AI Compare ung vien | Nha tuyen dung | So sanh nhieu ung vien | diem manh/yeu, ung vien uu tien |
| Interview Copilot | Nha tuyen dung / HR | Ho tro truoc va sau phong van | cau hoi, rubric, red flags, danh gia sau phong van |

## 3. Parse CV

### Y nghia

Parse CV la buoc nen de chuyen file CV thanh du lieu co cau truc. Neu buoc nay khong tot, cac tinh nang sau nhu matching, career report, chatbot, mock interview va shortlist se kem chinh xac.

### Input

- File PDF, DOC, DOCX.
- Hoac raw text tu CV builder.

### Xu ly

AI service doc file, trich xuat text, chuan hoa noi dung, sau do tim:

- Email.
- So dien thoai.
- Ten ung vien.
- Ky nang.
- Kinh nghiem.
- Hoc van.
- Diem tin cay parse.

### Ket qua

- `raw_text`
- `parsed_name`
- `parsed_email`
- `parsed_phone`
- `parsed_skills_json`
- `parsed_experience_json`
- `parsed_education_json`
- `confidence_score`

### Tai sao lam nhu vay

CV co nhieu dinh dang khac nhau. Luu file CV thoi la chua du; he thong can text va du lieu co cau truc de so khop voi JD va dua ra tu van.

### Toi uu them

- Them OCR cho PDF scan hoac CV dang anh.
- Cai thien doc file DOC cu.
- Detect layout 2 cot.
- Cho ung vien xem va sua du lieu parse.
- Chuan hoa skill theo skill catalog.

## 4. Parse JD

### Y nghia

Parse JD giup he thong hieu tin tuyen dung thay vi chi luu mo ta dang text.

### Input

- Tieu de tin.
- Mo ta cong viec.
- Yeu cau ung vien.
- Quyen loi.
- Luong, dia diem, cap bac, kinh nghiem.

### Ket qua

- Ky nang yeu cau.
- Yeu cau cong viec.
- Quyen loi.
- Thong tin luong.
- Dia diem.
- Raw text JD.

### Tai sao lam nhu vay

Matching can biet JD yeu cau ky nang gi, muc do nao, cap bac nao. Neu chi so sanh text thuan thi de bi nhieu boi canh gay nhieu.

### Toi uu them

- Tach ky nang bat buoc va ky nang uu tien.
- Gan trong so cho tung skill.
- Tu dong goi y skill khi nha tuyen dung tao tin.
- Canh bao JD qua ngan, mo ho hoac thieu yeu cau.

## 5. Semantic Search

### Y nghia

Semantic Search cho phep tim viec bang ngon ngu tu nhien. Vi du:

- "viec backend laravel cho fresher o TP HCM"
- "cong viec marketing can biet SEO va content"
- "intern data analyst co Power BI"

Khac voi tim kiem keyword thong thuong, Semantic Search co gang hieu y dinh, nhom nghe, ky nang va muc do lien quan.

### Luong xu ly

1. Nguoi dung nhap cau tim kiem.
2. Backend lay cac tin tuyen dung dang active, cong ty active, chua het han.
3. Backend gom thong tin job thanh document:
   - Tieu de.
   - Mo ta cong viec.
   - Dia diem.
   - Hinh thuc lam viec.
   - Cap bac.
   - Kinh nghiem.
   - Trinh do.
   - Ten cong ty.
   - Nganh nghe.
   - Ky nang yeu cau.
   - Parsed JD.
4. AI service tao vector cho query va documents.
5. Neu co `sentence_transformers` va `faiss` thi dung embedding + FAISS.
6. Neu khong co thi dung hashed vector fallback.
7. He thong rerank bang nhieu diem:
   - Semantic score.
   - Keyword score.
   - Skill score.
   - Category score.
   - Title score.
8. Backend luu/cap nhat vector vao bang `vector_embeddings`.
9. Tra ve job kem diem va ly do.

### Ket qua

Moi ket qua gom:

- `semantic_score`
- `keyword_score`
- `skill_score`
- `category_score`
- `title_score`
- `final_score`
- `semantic_reason`
- `matched_keywords`
- `job`

### Tai sao lam nhu vay

Nguoi tim viec khong phai luc nao cung biet dung keyword trong JD. Semantic Search giup tim duoc cac job gan nghia, cung nhom nghe, cung ky nang, ngay ca khi tu khoa khong trung 100%.

Thiet ke fallback hashed vector giup he thong van chay duoc khi moi truong chua cai embedding model hoac FAISS.

### Toi uu them

- Cai dat sentence-transformers + FAISS trong moi truong production de ket qua tot hon fallback.
- Cache embedding theo hash de khong phai tinh lai toan bo job moi lan search.
- Tach document thanh chunks neu JD dai.
- Ket hop filter cung: dia diem, luong, cap bac, hinh thuc lam viec.
- Hoc lai ranking tu hanh vi click/apply/save job cua ung vien.
- Them semantic search cho ung vien trong dashboard ca nhan dua tren CV.

## 6. Matched Jobs

### Y nghia

Matched Jobs so khop mot ho so ung vien voi cac tin tuyen dung de goi y viec phu hop.

### Xu ly

He thong dua CV profile va JD profile vao AI matching. Diem tong duoc tinh tu:

- Diem ky nang.
- Diem kinh nghiem.
- Diem hoc van.
- Diem tuong dong text.
- Trong so theo cap bac job.

Vi du, job senior se uu tien kinh nghiem cao hon job intern. Job intern/fresher se cho text similarity va hoc van co trong so hop ly hon.

### Ket qua

- `diem_phu_hop`
- `diem_ky_nang`
- `diem_kinh_nghiem`
- `diem_hoc_van`
- `chi_tiet_diem`
- `matched_skills_json`
- `missing_skills_json`
- `explanation`
- `danh_sach_ky_nang_thieu`

### Tai sao lam nhu vay

Neu chi dung keyword thi ket qua de sai. Neu chi dung LLM thi ton chi phi va kho kiem soat. Cach hien tai dung rule + semantic gan dung giup on dinh, nhanh va giai thich duoc.

### Toi uu them

- Dua semantic embedding vao matching skill.
- Hoc trong so tu du lieu tuyen dung that.
- Them diem luong, dia diem, hinh thuc lam viec.
- Giai thich chi tiet hon: vi sao diem thap, can bo sung gi.
- Them A/B testing giua cac model matching.

## 7. Career Report

### Y nghia

Career Report giup ung vien hieu minh phu hop voi huong nghe nao, nen bo sung ky nang gi va nen phat trien theo lo trinh nao.

### Input

- CV profile.
- Du lieu parse CV.
- Top matching jobs gan nhat.

### Ket qua

- `nghe_de_xuat`
- `muc_do_phu_hop`
- `goi_y_ky_nang_bo_sung`
- `bao_cao_chi_tiet`
- `model_version`

### Tai sao lam nhu vay

Ung vien khong chi can danh sach viec lam. Ho can biet ly do minh hop/khong hop, nen hoc gi va nen ung tuyen vao vai tro nao.

### Toi uu them

- Cho chon muc tieu: fresher, doi nganh, len senior, tang luong.
- Sinh roadmap 30/60/90 ngay.
- Goi y job va skill hoc tiep tu ket qua report.
- Luu nhieu phien ban report de so sanh tien bo.

## 8. Chatbot AI tu van nghe nghiep

### Y nghia

Chatbot la tro ly tu van hoi dap cho ung vien ve CV, viec lam, ky nang, dinh huong nghe nghiep va phong van.

### Xu ly

Chatbot dung:

- Lich su chat.
- Ho so ung vien.
- Career report gan nhat.
- Job lien quan neu co.
- Intent engine de phan loai cau hoi.
- Guardrail de chan cau hoi ngoai pham vi.
- Template fallback neu model loi.
- Streaming de tra loi muot hon.

### Ket qua

- Cau tra loi AI.
- Provider da dung.
- Intent.
- Thong tin guardrail neu co.
- Lich su hoi thoai.

### Tai sao lam nhu vay

Chatbot de ton chi phi neu moi cau deu goi LLM. Intent/template/fallback giup he thong nhanh, re va on dinh hon.

### Toi uu them

- Them RAG tu nganh nghe, ky nang, job, career report.
- Cho chatbot goi action: tao report, tao cover letter, bat dau mock interview.
- Them nut danh gia cau tra loi.
- Nho muc tieu nghe nghiep dai han cua user.

## 9. Mock Interview

### Y nghia

Mock Interview giup ung vien luyen phong van truoc khi ung tuyen hoac truoc lich phong van that.

### Tinh nang

- Tao phien phong van.
- Sinh cau hoi theo CV/JD.
- Danh gia cau tra loi.
- Sinh cau hoi tiep theo hoac follow-up.
- Tao bao cao tong ket.

### Rubric cham diem

- Ky thuat/chuyen mon.
- Giao tiep.
- Phu hop JD.
- Do ro rang.
- Tinh cu the.
- Cau truc cau tra loi.

### Ket qua

- Cau hoi phong van.
- Diem tung cau tra loi.
- Feedback chi tiet.
- Diem manh.
- Diem yeu.
- De xuat cai thien.
- Bao cao cuoi phien.

### Tai sao lam nhu vay

Phong van khong chi la dung/sai. Ung vien can tap cach trinh bay, dua vi du, lien ket kinh nghiem voi JD va tra loi co cau truc.

### Toi uu them

- Ho tro voice/audio.
- Cho chon cap do kho.
- Them interview mode: HR, technical, behavioral, case study.
- Cham theo STAR method.
- Phat hien cau tra loi qua ngan, chung chung hoac thieu bang chung.

## 10. Cover Letter AI

### Y nghia

Sinh thu xin viec ca nhan hoa theo CV, JD va diem matching.

### Input

- Ho so ung vien.
- Tin tuyen dung.
- Ket qua matching neu co.

### Ket qua

- `thu_xin_viec_ai`
- Metadata:
  - Ten ung vien.
  - Vi tri.
  - Cong ty.
  - Ky nang noi bat.
  - Ky nang thieu.
  - Diem phu hop.

### Tai sao lam nhu vay

Ung vien thuong viet cover letter chung chung. Dua CV, JD va matching vao prompt/context giup thu xin viec gan voi tin tuyen dung hon.

### Toi uu them

- Cho chon tone: trang trong, ngan gon, nhiet huyet.
- Sinh 2-3 phien ban.
- Kiem tra do chung chung.
- Goi y chinh sua truoc khi nop ho so.

## 11. CV Tailoring

### Y nghia

CV Tailoring giup tao phien ban CV phu hop voi mot JD cu the.

### Xu ly

He thong so sanh skill trong CV va skill trong JD, sau do:

- Doi title CV theo vi tri.
- Viet lai muc tieu nghe nghiep.
- Viet lai summary.
- Uu tien ky nang khop voi JD.
- Sap xep kinh nghiem/du an lien quan len truoc.
- Chi ra keyword khop va skill gap.

### Ket qua

- `tailored_profile`
- `matched_keywords`
- `skill_gaps`
- `recommendations`
- `cover_letter_suggestion`

### Tai sao lam nhu vay

Mot CV duy nhat kho toi uu cho moi job. Tailoring giup ung vien tao CV nham dung JD hon, tang kha nang qua vong loc.

### Toi uu them

- So sanh truoc/sau bang diem matching.
- Cho user chap nhan/tuchoi tung goi y.
- Kiem tra ATS-friendly.
- Khong tu them ky nang neu CV khong co bang chung.

## 12. CV Builder AI Writing

### Y nghia

Ho tro ung vien viet noi dung trong CV builder.

### Pham vi co the sinh

- Summary.
- Muc tieu nghe nghiep.
- Mo ta kinh nghiem.
- Mo ta du an.
- Ky nang.

### Ket qua

- Noi dung goi y theo section.
- Co the dua truc tiep vao CV builder.

### Tai sao lam nhu vay

Nguoi dung co the co kinh nghiem nhung khong biet viet thanh CV chuyen nghiep. AI Writing ho tro bien thong tin tho thanh cau chu ro rang hon.

### Toi uu them

- Cho chon do dai.
- Cho chon ngon ngu.
- Cho chon style theo nganh.
- Tu dong phat hien noi dung lap hoac qua chung.

## 13. AI Shortlist

### Y nghia

AI Shortlist giup nha tuyen dung loc nhanh ung vien phu hop voi mot tin tuyen dung.

### Xu ly

He thong lay tin tuyen dung, JD profile, danh sach ho so/ung tuyen, sau do xep hang theo do phu hop. Neu bat AI explanation, he thong sinh them giai thich cho tung ung vien.

### Ket qua

- Danh sach ung vien xep hang.
- Diem phu hop.
- Ky nang khop.
- Ky nang thieu.
- Giai thich AI.
- Confidence insight.

### Tai sao lam nhu vay

HR can rut ngan thoi gian doc CV. Shortlist giup tap trung vao nhom ung vien dang xem nhat.

### Toi uu them

- Cho HR chinh trong so.
- Them dieu kien bat buoc: dia diem, luong, so nam kinh nghiem, skill.
- Hoc tu hanh vi HR: shortlist, reject, interview, hire.
- Giai thich ro vi sao ung vien bi xep thap.

## 14. AI Compare ung vien

### Y nghia

AI Compare giup HR so sanh nhieu ung vien cho cung mot job.

### Ket qua

- Diem manh tung ung vien.
- Diem yeu/rui ro.
- Muc do phu hop voi JD.
- Goi y ung vien nen uu tien.

### Tai sao lam nhu vay

Sau shortlist, HR thuong phan van giua nhieu ung vien gan diem nhau. Compare giup quyet dinh dua tren tieu chi ro rang hon.

### Toi uu them

- Hien thi matrix so sanh.
- Cho chon tieu chi uu tien.
- Sinh cau hoi phong van rieng cho tung ung vien.
- Danh dau skill bat buoc chua dat.

## 15. Interview Copilot

### Y nghia

Interview Copilot la tro ly cho HR truoc va sau phong van.

### Generate truoc phong van

He thong sinh:

- Tom tat ung vien.
- Khu vuc can hoi sau.
- Nhom cau hoi phong van.
- Rubric cham diem.
- Red flags can chu y.

### Evaluate sau phong van

HR nhap ghi chu, diem rubric, quyet dinh du kien. He thong tra ve:

- Tom tat danh gia.
- Diem manh.
- Concern/rui ro.
- Next steps.
- Recommendation.

### Tai sao lam nhu vay

AI khong thay HR ra quyet dinh, ma giup HR phong van co cau truc, nhat quan va it cam tinh hon.

### Toi uu them

- Luu rubric theo tung vong phong van.
- Tu dong tao cau hoi theo red flags cua shortlist.
- Lien ket ket qua evaluate voi trang thai ung tuyen.
- Phat hien bias va canh bao khi danh gia thieu bang chung.

## 16. Billing, quota va log AI

### Free quota ung vien

- `cover_letter_generation`: 1 lan.
- `career_report_generation`: 1 lan.
- `chatbot_message`: 20 message.
- `mock_interview_session`: 1 session.

### Gia tinh nang ung vien

| Feature code | Ten | Gia |
|---|---|---|
| `cover_letter_generation` | Sinh thu xin viec AI | 3.000 VND/request |
| `career_report_generation` | Sinh bao cao dinh huong nghe nghiep | 5.000 VND/request |
| `chatbot_message` | Chatbot tu van nghe nghiep | 1.000 VND/message |
| `mock_interview_session` | Phien mock interview | 7.000 VND/session |

### Gia tinh nang nha tuyen dung

| Feature code | Ten | Gia |
|---|---|---|
| `employer_shortlist_ai_explanation` | AI Shortlist ung vien | 4.000 VND/request |
| `employer_candidate_compare_ai` | AI Compare ung vien | 6.000 VND/request |
| `interview_copilot_generate` | AI Interview Copilot | 5.000 VND/request |
| `interview_copilot_evaluate` | AI Evaluate Interview | 5.000 VND/request |

### Co che

He thong uu tien:

1. Subscription/quota neu co.
2. Free quota neu tinh nang co cau hinh.
3. Vi nguoi dung.

Neu AI loi, he thong co co che fail/release usage de tranh tru tien sai.

## 17. Diem manh hien tai

- Co day du pipeline tu CV/JD den matching, report, chat, interview.
- Co billing va free quota.
- Co fallback cho mot so tinh nang khi model/AI service loi.
- Co semantic search cho tim viec theo ngon ngu tu nhien.
- Co AI cho ca ung vien va nha tuyen dung.
- Co luu usage log de admin theo doi.
- Co giai thich ket qua o nhieu diem: matching, semantic search, shortlist.

## 18. Han che hien tai

- Parse CV PDF scan chua co OCR.
- Semantic Search co the dang dung hashed fallback neu chua cai sentence-transformers/faiss.
- Matching chua hoc tu du lieu tuyen dung thuc te.
- Chatbot chua co RAG day du tu knowledge base noi bo.
- Interview Copilot hien thien ve rule-based, chua phai LLM reasoning sau.
- Chua co co che user/HR danh gia chat luong output AI.
- Chua co dashboard chat luong model theo tung feature.

## 19. Huong toi uu uu tien

### Uu tien 1: Tang chat luong du lieu dau vao

- OCR cho CV scan.
- Chuan hoa skill catalog.
- Cho user sua parse result.
- Parse JD thanh bat buoc/uu tien/rui ro.

### Uu tien 2: Nang cap Semantic Search va Matching

- Cai sentence-transformers + FAISS.
- Cache embedding theo job.
- Chunk JD dai.
- Ket hop filter cung voi semantic score.
- Hoc ranking tu click/save/apply/interview/hire.

### Uu tien 3: Cai thien AI Assistant

- RAG cho chatbot.
- Tool calling noi bo: tao report, tao cover letter, mo mock interview.
- Luu memory ve muc tieu nghe nghiep.
- Thu thap feedback nguoi dung.

### Uu tien 4: Toi uu cho HR

- AI Shortlist co tuy chinh trong so.
- Compare ung vien dang matrix.
- Interview Copilot sinh cau hoi theo tung red flag.
- Ket noi ket qua phong van voi quyet dinh tuyen dung.

### Uu tien 5: Quan tri AI

- Dashboard chi phi theo feature.
- Ti le loi/fallback theo feature.
- Diem hai long nguoi dung.
- Lich su model_version.
- A/B testing prompt/model.

## 20. Ket luan

He thong hien tai da co mot bo tinh nang AI kha day du cho bai toan tuyen dung:

```text
CV/JD -> Parse -> Semantic Search/Matching -> Career Report/Chatbot/Mock Interview/Cover Letter/CV Tailoring
Ung tuyen -> AI Shortlist/Compare -> Interview Copilot -> Danh gia phong van
```

Trong do Semantic Search la lop tim kiem theo y dinh, Matched Jobs la lop so khop ca nhan hoa, Career Report va Chatbot la lop tu van, Mock Interview la lop luyen tap, AI Shortlist/Compare/Interview Copilot la lop ho tro nha tuyen dung ra quyet dinh nhanh va co cau truc hon.

Huong phat trien tot nhat tiep theo la nang chat luong du lieu dau vao, nang embedding/semantic ranking, them feedback loop tu hanh vi thuc te, va xay dashboard quan tri chat luong AI.
