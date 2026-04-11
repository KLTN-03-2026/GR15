<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\CongTy;
use App\Models\TinTuyenDung;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Storage;

class CongTyController extends Controller
{
    private function followedCompanyIds(Request $request): array
    {
        $user = $request->user();

        if (!$user || !$user->isUngVien()) {
            return [];
        }

        return $user->congTyTheoDois()->pluck('cong_tys.id')->map(fn ($id) => (int) $id)->all();
    }

    private function mapCompanyData(CongTy $congTy, array $followedCompanyIds = []): array
    {
        $data = $congTy->toArray();
        $data['logo_url'] = $congTy->logo
            ? url('/api/v1/cong-ty-logo?path=' . urlencode($congTy->logo))
            : null;
        $data['so_tin_dang_hoat_dong'] = (int) ($data['so_tin_dang_hoat_dong'] ?? 0);
        $data['so_nguoi_theo_doi'] = (int) ($data['so_nguoi_theo_doi'] ?? 0);
        $data['da_theo_doi'] = in_array((int) $congTy->id, $followedCompanyIds, true);

        return $data;
    }

    public function index(Request $request): JsonResponse
    {
        $followedCompanyIds = $this->followedCompanyIds($request);

        $query = CongTy::query()
            ->with('nganhNghe:id,ten_nganh')
            ->withCount([
                'nguoiDungTheoDois as so_nguoi_theo_doi',
                'tinTuyenDungs as so_tin_dang_hoat_dong' => function ($subQuery) {
                    $subQuery->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
                        ->where(function ($nestedQuery) {
                            $nestedQuery->whereNull('ngay_het_han')
                                ->orWhere('ngay_het_han', '>=', now());
                        });
                },
            ])
            ->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG);

        if ($request->filled('search')) {
            $search = trim((string) $request->input('search'));
            $query->where(function ($subQuery) use ($search) {
                $subQuery->where('ten_cong_ty', 'like', "%{$search}%")
                    ->orWhere('dia_chi', 'like', "%{$search}%");
            });
        }

        $query->orderBy('ten_cong_ty');

        $perPage = (int) $request->get('per_page', 0);
        $data = $perPage > 0 ? $query->paginate(min($perPage, 100)) : $query->get();

        if ($data instanceof LengthAwarePaginator) {
            $data->setCollection($data->getCollection()->map(fn ($item) => $this->mapCompanyData($item, $followedCompanyIds)));
        } else {
            $data = $data->map(fn ($item) => $this->mapCompanyData($item, $followedCompanyIds));
        }

        return response()->json([
            'success' => true,
            'data' => $data,
        ]);
    }

    public function show(Request $request, int $id): JsonResponse
    {
        $followedCompanyIds = $this->followedCompanyIds($request);

        $congTy = CongTy::query()
            ->with([
                'nganhNghe:id,ten_nganh',
                'nguoiDung:id,ho_ten,email',
                'tinTuyenDungs' => function ($query) {
                    $query->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
                        ->where(function ($nestedQuery) {
                            $nestedQuery->whereNull('ngay_het_han')
                                ->orWhere('ngay_het_han', '>=', now());
                        })
                        ->withCount(['acceptedApplications as so_luong_da_nhan'])
                        ->orderByDesc('created_at')
                        ->limit(6);
                },
            ])
            ->withCount([
                'nguoiDungTheoDois as so_nguoi_theo_doi',
                'tinTuyenDungs as so_tin_dang_hoat_dong' => function ($query) {
                    $query->where('trang_thai', TinTuyenDung::TRANG_THAI_HOAT_DONG)
                        ->where(function ($nestedQuery) {
                            $nestedQuery->whereNull('ngay_het_han')
                                ->orWhere('ngay_het_han', '>=', now());
                        });
                },
            ])
            ->where('trang_thai', CongTy::TRANG_THAI_HOAT_DONG)
            ->findOrFail($id);

        return response()->json([
            'success' => true,
            'data' => $this->mapCompanyData($congTy, $followedCompanyIds),
        ]);
    }

    public function logo(Request $request)
    {
        $path = (string) $request->query('path', '');

        abort_unless($path !== '' && str_starts_with($path, 'cong_ty_logos/'), 404);
        abort_unless(Storage::disk('public')->exists($path), 404);

        return response()->file(Storage::disk('public')->path($path));
    }
}
