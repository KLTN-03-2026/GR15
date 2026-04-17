<?php

use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\AiChatMessageController;
use App\Http\Controllers\Api\AiChatSessionController;
use App\Http\Controllers\Api\CareerReportController;
use App\Http\Controllers\Api\HoSoController;
use App\Http\Controllers\Api\KyNangController;
use App\Http\Controllers\Api\MatchingController;
use App\Http\Controllers\Api\MockInterviewController;
use App\Http\Controllers\Api\NguoiDungKyNangController;
use App\Http\Controllers\Api\TinTuyenDungController;
use App\Http\Controllers\Api\UngVienKetQuaMatchingController;
use App\Http\Controllers\Api\UngVienTuVanNgheNghiepController;
use App\Http\Controllers\Api\Admin\AdminKetQuaMatchingController;
use Illuminate\Support\Facades\Route;

Route::post('v1/dang-ky', [AuthController::class, 'dangKy'])->name('auth.dang-ky');
Route::post('v1/dang-nhap', [AuthController::class, 'dangNhap'])->name('auth.dang-nhap');
Route::post('v1/quen-mat-khau', [AuthController::class, 'quenMatKhau'])->name('auth.quen-mat-khau');
Route::post('v1/dat-lai-mat-khau', [AuthController::class, 'datLaiMatKhau'])->name('auth.dat-lai-mat-khau');
Route::post('v1/gui-lai-email-xac-thuc', [AuthController::class, 'guiLaiEmailXacThuc'])->name('auth.gui-lai-email-xac-thuc');
Route::get('v1/xac-thuc-email/{id}/{hash}', [AuthController::class, 'xacThucEmail'])
    ->middleware('signed')
    ->name('verification.verify');
Route::get('v1/anh-dai-dien', [AuthController::class, 'avatar'])->name('auth.avatar');
Route::get('v1/chung-chi-ky-nang', [NguoiDungKyNangController::class, 'hinhAnh'])->name('ung-vien.ky-nangs.hinh-anh');

Route::get('v1/ky-nangs', [KyNangController::class, 'index'])->name('ky-nangs.index');
Route::get('v1/ky-nangs/{id}', [KyNangController::class, 'show'])->name('ky-nangs.show');
Route::get('v1/tin-tuyen-dungs', [TinTuyenDungController::class, 'index'])->name('tin-tuyen-dungs.index');
Route::get('v1/tin-tuyen-dungs/{id}', [TinTuyenDungController::class, 'show'])->name('tin-tuyen-dungs.show');

Route::middleware('auth:sanctum')->group(function (): void {
    Route::post('v1/dang-xuat', [AuthController::class, 'dangXuat'])->name('auth.dang-xuat');
    Route::get('v1/ho-so', [AuthController::class, 'hoSo'])->name('auth.ho-so');
    Route::put('v1/ho-so', [AuthController::class, 'capNhatHoSo'])->name('auth.cap-nhat-ho-so');
    Route::post('v1/doi-mat-khau', [AuthController::class, 'doiMatKhau'])->name('auth.doi-mat-khau');

    Route::middleware('role:ung_vien')->group(function (): void {
        Route::get('v1/ung-vien/ho-sos', [HoSoController::class, 'index'])->name('ung-vien.ho-sos.index');
        Route::post('v1/ung-vien/ho-sos', [HoSoController::class, 'store'])->name('ung-vien.ho-sos.store');
        Route::get('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'show'])->name('ung-vien.ho-sos.show');
        Route::put('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'update'])->name('ung-vien.ho-sos.update');
        Route::delete('v1/ung-vien/ho-sos/{id}', [HoSoController::class, 'destroy'])->name('ung-vien.ho-sos.destroy');
        Route::patch('v1/ung-vien/ho-sos/{id}/trang-thai', [HoSoController::class, 'doiTrangThai'])->name('ung-vien.ho-sos.doi-trang-thai');

        Route::post('v1/ung-vien/ho-sos/{id}/matching', [MatchingController::class, 'generate'])->name('ung-vien.ho-sos.matching');
        Route::post('v1/ung-vien/ho-sos/{id}/career-report', [CareerReportController::class, 'generate'])->name('ung-vien.ho-sos.career-report');

        Route::get('v1/ai-chat/sessions', [AiChatSessionController::class, 'index'])->name('ai-chat.sessions.index');
        Route::post('v1/ai-chat/sessions', [AiChatSessionController::class, 'store'])->name('ai-chat.sessions.store');
        Route::patch('v1/ai-chat/sessions/{id}/status', [AiChatSessionController::class, 'updateStatus'])->name('ai-chat.sessions.update-status');
        Route::get('v1/ai-chat/sessions/{id}/messages', [AiChatSessionController::class, 'messages'])->name('ai-chat.sessions.messages');
        Route::delete('v1/ai-chat/sessions/{id}/messages', [AiChatSessionController::class, 'clearMessages'])->name('ai-chat.sessions.clear-messages');
        Route::post('v1/ai-chat/messages', [AiChatMessageController::class, 'store'])->name('ai-chat.messages.store');
        Route::post('v1/ai-chat/messages/stream', [AiChatMessageController::class, 'stream'])->name('ai-chat.messages.stream');

        Route::get('v1/mock-interview/sessions', [MockInterviewController::class, 'index'])->name('mock-interview.sessions.index');
        Route::get('v1/mock-interview/dashboard', [MockInterviewController::class, 'dashboard'])->name('mock-interview.dashboard');
        Route::post('v1/mock-interview/sessions', [MockInterviewController::class, 'store'])->name('mock-interview.sessions.store');
        Route::get('v1/mock-interview/sessions/{id}/messages', [MockInterviewController::class, 'messages'])->name('mock-interview.sessions.messages');
        Route::patch('v1/mock-interview/sessions/{id}/status', [MockInterviewController::class, 'updateStatus'])->name('mock-interview.sessions.update-status');
        Route::delete('v1/mock-interview/sessions/{id}', [MockInterviewController::class, 'clearSession'])->name('mock-interview.sessions.destroy');
        Route::post('v1/mock-interview/messages', [MockInterviewController::class, 'answer'])->name('mock-interview.messages.answer');
        Route::post('v1/mock-interview/messages/stream', [MockInterviewController::class, 'stream'])->name('mock-interview.messages.stream');
        Route::post('v1/mock-interview/sessions/{id}/report', [MockInterviewController::class, 'generateReport'])->name('mock-interview.sessions.report.generate');
        Route::post('v1/mock-interview/sessions/{id}/report/stream', [MockInterviewController::class, 'streamReport'])->name('mock-interview.sessions.report.stream');
        Route::get('v1/mock-interview/sessions/{id}/report', [MockInterviewController::class, 'showReport'])->name('mock-interview.sessions.report.show');

        Route::get('v1/ung-vien/ket-qua-matchings', [UngVienKetQuaMatchingController::class, 'index'])->name('ung-vien.ket-qua-matchings.index');
        Route::get('v1/ung-vien/tu-van-nghe-nghieps', [UngVienTuVanNgheNghiepController::class, 'index'])->name('ung-vien.tu-van-nghe-nghieps.index');

        Route::get('v1/ung-vien/ky-nangs', [NguoiDungKyNangController::class, 'index'])->name('ung-vien.ky-nangs.index');
        Route::post('v1/ung-vien/ky-nangs', [NguoiDungKyNangController::class, 'store'])->name('ung-vien.ky-nangs.store');
        Route::post('v1/ung-vien/ky-nangs/{id}', [NguoiDungKyNangController::class, 'update'])->name('ung-vien.ky-nangs.update.multipart');
        Route::put('v1/ung-vien/ky-nangs/{id}', [NguoiDungKyNangController::class, 'update'])->name('ung-vien.ky-nangs.update');
        Route::delete('v1/ung-vien/ky-nangs/{id}', [NguoiDungKyNangController::class, 'destroy'])->name('ung-vien.ky-nangs.destroy');
    });

    Route::middleware('role:admin')->group(function (): void {
        Route::get('v1/admin/ket-qua-matchings/thong-ke', [AdminKetQuaMatchingController::class, 'thongKe'])->name('admin.ket-qua-matchings.thong-ke');
        Route::get('v1/admin/ket-qua-matchings', [AdminKetQuaMatchingController::class, 'index'])->name('admin.ket-qua-matchings.index');
    });
});
