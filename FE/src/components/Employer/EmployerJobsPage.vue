<template>
    <div class="max-w-7xl mx-auto w-full">
        <!-- Page Header -->
        <div class="flex flex-wrap items-end justify-between gap-4 mb-8">
            <div class="flex flex-col gap-1">
                <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Danh sách tin tuyển dụng
                </h1>
                <p class="text-slate-500 dark:text-slate-400 text-sm">Tạo, quản lý và theo dõi các tin tuyển dụng đang
                    hoạt động.</p>
            </div>
            <button
                class="flex items-center justify-center gap-2 rounded-lg h-11 px-6 bg-[#2463eb] text-white hover:bg-blue-700 transition-colors font-semibold shadow-lg shadow-[#2463eb]/20">
                <span class="material-symbols-outlined text-[20px]">add</span>
                <span>Đăng tin mới</span>
            </button>
        </div>

        <!-- Stats Bar -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div
                class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Đang tuyển</p>
                <p class="text-2xl font-black text-slate-900 dark:text-white">12</p>
            </div>
            <div
                class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Tổng ứng viên</p>
                <p class="text-2xl font-black text-slate-900 dark:text-white">482</p>
            </div>
            <div
                class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Đã lên lịch PV</p>
                <p class="text-2xl font-black text-slate-900 dark:text-white">34</p>
            </div>
            <div
                class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-1">Tuyển trong tháng</p>
                <p class="text-2xl font-black text-slate-900 dark:text-white">5</p>
            </div>
        </div>

        <!-- Tabs & Table -->
        <div
            class="flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
            <div class="flex border-b border-slate-200 dark:border-slate-800 px-4">
                <a class="flex items-center gap-2 border-b-2 border-[#2463eb] text-[#2463eb] px-4 pb-3 pt-4 font-bold text-sm"
                    href="#">
                    Đang tuyển <span class="bg-[#2463eb]/10 px-1.5 py-0.5 rounded text-[10px]">8</span>
                </a>
                <a class="flex items-center gap-2 border-b-2 border-transparent text-slate-500 px-4 pb-3 pt-4 font-medium text-sm hover:text-slate-700 dark:hover:text-slate-300"
                    href="#">
                    Bản nháp <span class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-[10px]">3</span>
                </a>
                <a class="flex items-center gap-2 border-b-2 border-transparent text-slate-500 px-4 pb-3 pt-4 font-medium text-sm hover:text-slate-700 dark:hover:text-slate-300"
                    href="#">
                    Đã đóng <span class="bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-[10px]">24</span>
                </a>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                            <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Vị trí</th>
                            <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Ngành</th>
                            <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Ứng viên
                            </th>
                            <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500">Status</th>
                            <th class="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 text-right">
                                Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm font-semibold text-slate-900 dark:text-white">Senior Frontend
                                        Engineer</span>
                                    <span class="text-xs text-slate-500">Posted 2 days ago</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Technology</span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-bold text-slate-900 dark:text-white">42</span>
                                    <span class="text-[10px] text-green-600 font-bold">+5 new</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center gap-1.5 rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-1 text-xs font-bold text-green-700 dark:text-green-400">
                                    <span class="size-1.5 rounded-full bg-green-600"></span>
                                    Đang tuyển
                                </span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex justify-end gap-2">
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-[#2463eb] hover:bg-[#2463eb]/10 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">edit</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">delete</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">more_vert</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm font-semibold text-slate-900 dark:text-white">Product
                                        Designer</span>
                                    <span class="text-xs text-slate-500">Posted 5 days ago</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Design</span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-bold text-slate-900 dark:text-white">15</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center gap-1.5 rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-1 text-xs font-bold text-green-700 dark:text-green-400">
                                    <span class="size-1.5 rounded-full bg-green-600"></span>
                                    Đang tuyển
                                </span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex justify-end gap-2">
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-[#2463eb] hover:bg-[#2463eb]/10 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">edit</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">delete</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">more_vert</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm font-semibold text-slate-900 dark:text-white">Marketing
                                        Manager</span>
                                    <span class="text-xs text-slate-500">Last edited 1 hour ago</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Marketing</span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-bold text-slate-400 dark:text-slate-600">0</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center gap-1.5 rounded-full bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-bold text-slate-600 dark:text-slate-400">
                                    <span class="size-1.5 rounded-full bg-slate-400"></span>
                                    Bản nháp
                                </span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex justify-end gap-2">
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-[#2463eb] hover:bg-[#2463eb]/10 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">edit</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">delete</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">more_vert</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm font-semibold text-slate-900 dark:text-white">Data
                                        Analyst</span>
                                    <span class="text-xs text-slate-500">Đóng 1 tuần trước</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Data
                                    Science</span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-bold text-slate-900 dark:text-white">89</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center gap-1.5 rounded-full bg-red-100 dark:bg-red-900/30 px-2 py-1 text-xs font-bold text-red-700 dark:text-red-400">
                                    <span class="size-1.5 rounded-full bg-red-600"></span>
                                    Đã đóng
                                </span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex justify-end gap-2">
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-[#2463eb] hover:bg-[#2463eb]/10 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">visibility</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">more_vert</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                            <td class="px-6 py-4">
                                <div class="flex flex-col">
                                    <span class="text-sm font-semibold text-slate-900 dark:text-white">QA
                                        Specialist</span>
                                    <span class="text-xs text-slate-500">Posted 10 days ago</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-1 text-xs font-medium text-slate-600 dark:text-slate-400">Technology</span>
                            </td>
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <span class="text-sm font-bold text-slate-900 dark:text-white">28</span>
                                </div>
                            </td>
                            <td class="px-6 py-4">
                                <span
                                    class="inline-flex items-center gap-1.5 rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-1 text-xs font-bold text-green-700 dark:text-green-400">
                                    <span class="size-1.5 rounded-full bg-green-600"></span>
                                    Đang tuyển
                                </span>
                            </td>
                            <td class="px-6 py-4 text-right">
                                <div class="flex justify-end gap-2">
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-[#2463eb] hover:bg-[#2463eb]/10 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">edit</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">delete</span>
                                    </button>
                                    <button
                                        class="size-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600 transition-colors">
                                        <span class="material-symbols-outlined text-[18px]">more_vert</span>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div
                class="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 px-6 py-4 bg-slate-50/50 dark:bg-slate-900">
                <p class="text-xs text-slate-500 font-medium">Hiển thị 1 đến 5 trong tổng số 8 tin đang tuyển</p>
                <div class="flex gap-2">
                    <button
                        class="px-3 py-1 rounded-md border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-white transition-colors disabled:opacity-50"
                        disabled>Trước</button>
                    <button
                        class="px-3 py-1 rounded-md border border-slate-200 dark:border-slate-700 text-xs font-bold text-slate-600 dark:text-slate-400 hover:bg-white transition-colors">Sau</button>
                </div>
            </div>
        </div>

        <!-- Footer CTA -->
        <div
            class="mt-8 p-6 rounded-2xl bg-gradient-to-r from-[#2463eb] to-blue-600 text-white flex flex-col md:flex-row items-center justify-between gap-6 overflow-hidden relative">
            <div class="flex flex-col gap-2 z-10">
                <h3 class="text-xl font-bold">Cần hỗ trợ cho quy trình tuyển dụng?</h3>
                <p class="text-blue-100 text-sm max-w-md">Đội ngũ tư vấn nhân sự của chúng tôi có thể giúp bạn tối ưu JD
                    và tiếp cận nhiều ứng viên phù hợp hơn.</p>
            </div>
            <button
                class="whitespace-nowrap bg-white text-[#2463eb] px-6 py-2.5 rounded-lg font-bold hover:bg-blue-50 transition-colors shadow-lg z-10">
                Đặt lịch tư vấn
            </button>
            <!-- Background Decoration -->
            <div class="absolute right-0 top-0 w-64 h-64 bg-white/10 rounded-full -mr-24 -mt-24 blur-3xl"></div>
            <div class="absolute left-0 bottom-0 w-32 h-32 bg-blue-400/20 rounded-full -ml-16 -mb-16 blur-2xl"></div>
        </div>
    </div>
</template>

<script setup>
</script>
