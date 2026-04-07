<?php

namespace Database\Factories;

use App\Models\KyNang;
use Illuminate\Database\Eloquent\Factories\Factory;

class KyNangFactory extends Factory
{
    protected $model = KyNang::class;

    public function definition(): array
    {
        $ten = $this->faker->unique()->randomElement([
            'Machine Learning',
            'Blockchain',
            'Cloud Computing',
            'Data Engineering',
            'UI/UX Research',
            'Growth Hacking',
            'Scrum Master',
            'Technical Writing',
            'GraphQL',
        ]);

        return [
            'ten_ky_nang' => $ten,
            'so_chung_chi' => $this->faker->numberBetween(0, 5),
            'hinh_anh' => null,
        ];
    }
}
