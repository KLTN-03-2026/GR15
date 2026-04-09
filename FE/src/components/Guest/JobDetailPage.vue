<template>
  <div class="max-w-7xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Main Content Left Column -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Job Header Card -->
        <div class="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
          <div class="flex flex-col md:flex-row md:items-start gap-6">
            <div class="w-20 h-20 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center overflow-hidden flex-shrink-0"></div>
            <div class="flex-grow">
              <h2 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-2">Senior Software Engineer</h2>
              <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-slate-600 dark:text-slate-400">
                <div class="flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-lg">corporate_fare</span>
                  <span class="font-medium text-slate-900 dark:text-slate-200">TechFlow Solutions</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-lg">location_on</span>
                  <span>San Francisco, CA (Remote Friendly)</span>
                </div>
              </div>
              <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 py-6 border-y border-slate-100 dark:border-slate-800">
                <div>
                  <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">Salary range</p>
                  <p class="font-semibold text-slate-900 dark:text-white">$150k - $200k</p>
                </div>
                <div>
                  <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">Openings</p>
                  <p class="font-semibold text-slate-900 dark:text-white">2 Positions</p>
                </div>
                <div>
                  <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">Job Type</p>
                  <p class="font-semibold text-slate-900 dark:text-white">Full-time</p>
                </div>
                <div>
                  <p class="text-xs uppercase tracking-wider text-slate-400 font-bold mb-1">Deadline</p>
                  <p class="font-semibold text-red-500">Oct 30, 2024</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Job Description Section -->
        <div class="bg-white dark:bg-slate-900 p-6 md:p-8 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
          <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-4">About the Role</h3>
          <div class="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 leading-relaxed space-y-4">
            <p>TechFlow Solutions is looking for a Senior Software Engineer to lead our core architecture team. You will be responsible for designing and implementing scalable backend services that power our global analytics platform.</p>
            <p>We are looking for someone who is passionate about building high-performance systems and enjoys mentoring junior developers.</p>
            <h4 class="text-lg font-semibold text-slate-900 dark:text-white pt-2">What you'll do</h4>
            <ul class="list-disc pl-5 space-y-2">
              <li>Develop and maintain scalable backend services using Node.js and Go.</li>
              <li>Architect microservices and manage their deployment across multi-region AWS environments.</li>
              <li>Collaborate with cross-functional teams to define, design, and ship new features.</li>
              <li>Participate in code reviews and advocate for engineering best practices.</li>
              <li>Implement robust monitoring and logging for production systems.</li>
            </ul>
          </div>
          <div class="mt-8">
            <h4 class="text-sm font-bold uppercase tracking-widest text-slate-400 mb-4">Kỹ năng yêu cầu</h4>
            <div class="flex flex-wrap gap-2">
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">Node.js</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">Go</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">TypeScript</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">PostgreSQL</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">Docker</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">AWS</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">Kubernetes</span>
              <span class="px-3 py-1.5 bg-[#2463eb]/10 text-[#2463eb] text-sm font-medium rounded-lg border border-[#2463eb]/20">Microservices</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Sidebar: AI Matching -->
      <div class="lg:col-span-4 space-y-6">
        <div class="bg-white dark:bg-slate-900 rounded-xl shadow-lg border-2 border-[#2463eb]/30 overflow-hidden">
          <div class="bg-[#2463eb] p-6 text-white">
            <div class="flex items-center gap-2 mb-1">
              <span class="material-symbols-outlined">auto_awesome</span>
              <h3 class="font-bold text-lg">Phân tích phù hợp từ AI</h3>
            </div>
            <p class="text-sm opacity-90">Dựa trên hồ sơ và CV của bạn</p>
          </div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-2">
              <span class="text-slate-900 dark:text-white font-bold">Điểm phù hợp</span>
              <span class="text-[#2463eb] font-bold text-xl">82%</span>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-3 mb-4">
              <div class="bg-[#2463eb] h-3 rounded-full" style="width: 82%"></div>
            </div>
            <div class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 mb-6">
              <span class="material-symbols-outlined text-sm mr-1">check_circle</span>
              Mức phù hợp cao
            </div>
            <div class="space-y-4">
              <h4 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-orange-500 text-lg">warning</span>
                Phân tích khoảng trống kỹ năng
              </h4>
              <p class="text-sm text-slate-500 dark:text-slate-400">Tăng cơ hội của bạn bằng cách làm nổi bật các kỹ năng này:</p>
              <ul class="space-y-3">
                <li class="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                  <span class="w-2 h-2 rounded-full bg-orange-500"></span>
                  <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Docker</span>
                  <span class="ml-auto text-[10px] font-bold uppercase text-slate-400">Quan trọng</span>
                </li>
                <li class="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                  <span class="w-2 h-2 rounded-full bg-orange-500"></span>
                  <span class="text-sm font-medium text-slate-700 dark:text-slate-300">AWS (S3, EC2, Lambda)</span>
                  <span class="ml-auto text-[10px] font-bold uppercase text-slate-400">Thiết yếu</span>
                </li>
                <li class="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                  <span class="w-2 h-2 rounded-full bg-orange-500"></span>
                  <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Microservices Architecture</span>
                  <span class="ml-auto text-[10px] font-bold uppercase text-slate-400">Ưu tiên</span>
                </li>
              </ul>
            </div>
            <div class="mt-8 space-y-3">
              <button class="w-full bg-[#2463eb] hover:bg-[#2463eb]/90 text-white font-bold py-4 rounded-xl shadow-lg shadow-[#2463eb]/30 flex items-center justify-center gap-2 transition-all transform active:scale-[0.98]">
                Ứng tuyển ngay
                <span class="material-symbols-outlined">arrow_forward</span>
              </button>
              <button class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-bold py-4 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                Lưu việc làm
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
