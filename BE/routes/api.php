<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\CongTyController;
use App\Http\Controllers\Api\HoSoController;
use App\Http\Controllers\Api\KyNangController;
use App\Http\Controllers\Api\NganhNgheController;
use App\Http\Controllers\Api\NguoiDungKyNangController;
use App\Http\Controllers\Api\SemanticSearchController;
use App\Http\Controllers\Api\TinTuyenDungController;
use App\Http\Controllers\Api\UngVienKetQuaMatchingController;
use App\Http\Controllers\Api\UngVienLuuTinController;
use App\Http\Controllers\Api\UngVienTheoDoiCongTyController;
use App\Http\Controllers\Api\UngVienTuVanNgheNghiepController;
use App\Http\Controllers\Api\UngVienUngTuyenController;
use Illuminate\Support\Facades\Route;

Route::post('v1/dang-ky', [AuthController::class, 'dangKy']);
Route::post('v1/dang-nhap', [AuthController::class, 'dangNhap']);
Route::post('v1/quen-mat-khau', [AuthController::class, 'quenMatKhau']);
Route::post('v1/dat-lai-mat-khau', [AuthController::class, 'datLaiMatKhau']);

Route::get('v1/anh-dai-dien', [AuthController::class, 'avatar']);
Route::get('v1/cong-ty-logo', [CongTyController::class, 'logo']);
Route::get('v1/chung-chi-ky-nang', [NguoiDungKyNangController::class, 'hinhAnh']);

Route::get('v1/tin-tuyen-dungs/semantic-search', [SemanticSearchController::class, 'searchJobs']);
Route::get('v1/tin-tuyen-dungs', [TinTuyenDungController::class, 'index']);
Route::get('v1/tin-tuyen-dungs/{id}', [TinTuyenDungController::class, 'show']);
Route::get('v1/cong-tys', [CongTyController::class, 'index']);
Route::get('v1/cong-tys/{id}', [CongTyController::class, 'show']);
Route::get('v1/nganh-nghes', [NganhNgheController::class, 'index']);
Route::get('v1/nganh-nghes/{id}', [NganhNgheController::class, 'show']);
Route::get('v1/ky-nangs', [KyNangController::class, 'index']);
Route::get('v1/ky-nangs/{id}', [KyNangController::class, 'show']);

Route::middleware('auth.api')->group(function () {
    Route::post('v1/dang-xuat', [AuthController::class, 'dangXuat']);
    Route::get('v1/ho-so', [AuthController::class, 'hoSo']);
    Route::put('v1/ho-so', [AuthController::class, 'capNhatHoSo']);
    Route::post('v1/doi-mat-khau', [AuthController::class, 'doiMatKhau']);

    Route::get('v1/ung-vien/tin-da-luu', [UngVienLuuTinController::class, 'index']);
    Route::post('v1/ung-vien/tin-da-luu/{tin_id}/toggle', [UngVienLuuTinController::class, 'toggle']);
    Route::get('v1/ung-vien/cong-ty-theo-doi', [UngVienTheoDoiCongTyController::class, 'index']);
    Route::post('v1/ung-vien/cong-ty-theo-doi/{cong_ty_id}/toggle', [UngVienTheoDoiCongTyController::class, 'toggle']);
    Route::get('v1/ung-vien/ung-tuyens', [UngVienUngTuyenController::class, 'index']);
    Route::post('v1/ung-vien/ung-tuyens', [UngVienUngTuyenController::class, 'store']);
    Route::patch('v1/ung-vien/ung-tuyens/{id}', [UngVienUngTuyenController::class, 'update']);
    Route::patch('v1/ung-vien/ung-tuyens/{id}/xac-nhan-phong-van', [UngVienUngTuyenController::class, 'xacNhanPhongVan']);
    Route::patch('v1/ung-vien/ung-tuyens/{id}/rut-don', [UngVienUngTuyenController::class, 'rutDon']);
    Route::get('v1/ung-vien/ky-nangs', [NguoiDungKyNangController::class, 'index']);
    Route::post('v1/ung-vien/ky-nangs', [NguoiDungKyNangController::class, 'store']);
    Route::put('v1/ung-vien/ky-nangs/{id}', [NguoiDungKyNangController::class, 'update']);
    Route::delete('v1/ung-vien/ky-nangs/{id}', [NguoiDungKyNangController::class, 'destroy']);
    Route::get('v1/ung-vien/ket-qua-matchings', [UngVienKetQuaMatchingController::class, 'index']);
    Route::get('v1/ung-vien/tu-van-nghe-nghieps', [UngVienTuVanNgheNghiepController::class, 'index']);

    Route::get('v1/ung-vien/ho-sos', [HoSoController::class, 'index']);
    Route::post('v1/ung-vien/ho-sos', [HoSoController::class, 'store']);
    Route::get('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'show']);
    Route::put('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'update']);
    Route::delete('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'destroy']);
    Route::patch('v1/ung-vien/ho-sos/{id}/trang-thai', [HoSoController::class, 'doiTrangThai']);
    Route::post('v1/ung-vien/ho-sos/{id}/parse', [HoSoController::class, 'parse']);
    Route::post('v1/ung-vien/ho-sos/{id}/matching', [HoSoController::class, 'generateMatching']);
    Route::post('v1/ung-vien/ho-sos/{id}/career-report', [HoSoController::class, 'generateCareerReport']);
});
