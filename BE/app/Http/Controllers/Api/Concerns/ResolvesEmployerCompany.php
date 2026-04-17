<?php

namespace App\Http\Controllers\Api\Concerns;

use App\Models\CongTy;
use App\Models\NguoiDung;

trait ResolvesEmployerCompany
{
    protected function getAuthenticatedEmployer(): ?NguoiDung
    {
        /** @var NguoiDung|null $user */
        $user = auth()->user();

        return $user;
    }

    protected function getCurrentEmployerCompany(): ?CongTy
    {
        $user = $this->getAuthenticatedEmployer();

        return $user?->congTyHienTai();
    }

    protected function isCompanyOwner(?NguoiDung $user, ?CongTy $congTy): bool
    {
        if (!$user || !$congTy) {
            return false;
        }

        return $user->laChuSoHuuCongTy($congTy->id);
    }
}
