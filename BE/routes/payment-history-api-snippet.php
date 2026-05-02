<?php

use App\Http\Controllers\Api\PaymentHistoryController;
use Illuminate\Support\Facades\Route;

Route::get('v1/ung-vien/payments', [PaymentHistoryController::class, 'index'])
    ->middleware(['auth:sanctum', 'role:ung_vien'])
    ->name('ung-vien.payments.index');

Route::get('v1/ung-vien/payments/{maGiaoDichNoiBo}', [PaymentHistoryController::class, 'show'])
    ->middleware(['auth:sanctum', 'role:ung_vien'])
    ->name('ung-vien.payments.show');
