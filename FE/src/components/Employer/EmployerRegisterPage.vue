<template>
    <div class="flex-1 flex items-center justify-center p-4 md:p-10">
        <!-- Message Alert -->
        <div v-if="errorMessage || successMessage" class="fixed top-20 left-0 right-0 mx-auto max-w-[450px] z-50">
            <div v-if="errorMessage"
                class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-200 px-6 py-3 rounded-lg flex items-center gap-2">
                <span class="material-symbols-outlined text-lg">error</span>
                <span>{{ errorMessage }}</span>
            </div>
            <div v-if="successMessage"
                class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 text-green-700 dark:text-green-200 px-6 py-3 rounded-lg flex items-center gap-2">
                <span class="material-symbols-outlined text-lg">check_circle</span>
                <span>{{ successMessage }}</span>
            </div>
        </div>

        <!-- Register Card -->
        <div class="w-full max-w-[450px] bg-white dark:bg-slate-900 rounded-xl shadow-xl p-8 md:p-12">
            <!-- Header -->
            <div class="mb-8 text-center">
                <div class="flex justify-center mb-4">
                    <span class="material-symbols-outlined text-5xl text-[#2463eb]">business</span>
                </div>
                <h1 class="text-3xl font-black tracking-tight mb-2">Đăng ký Doanh Nghiệp</h1>
                <p class="text-slate-500 dark:text-slate-400">Tuyển dụng nhân tài hàng đầu</p>
            </div>

            <!-- Register Form -->
            <form class="space-y-4" @submit.prevent="handleRegister">
                <!-- Company Name -->
                <div>
                    <label class="block text-sm font-semibold mb-1">Tên công ty <span
                            class="text-red-500">*</span></label>
                    <input v-model="registerForm.companyName" :class="{
                        'border-red-500 dark:border-red-500': registerErrors.companyName,
                        'border-slate-200 dark:border-slate-700': !registerErrors.companyName
                    }" class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors"
                        placeholder="Tên công ty của bạn" type="text" :disabled="isLoading" />
                    <span v-if="registerErrors.companyName" class="text-red-500 text-xs mt-1 block">{{
                        registerErrors.companyName
                        }}</span>
                </div>

                <!-- Contact Person -->
                <div>
                    <label class="block text-sm font-semibold mb-1">Người liên hệ <span
                            class="text-red-500">*</span></label>
                    <input v-model="registerForm.contactPerson" :class="{
                        'border-red-500 dark:border-red-500': registerErrors.contactPerson,
                        'border-slate-200 dark:border-slate-700': !registerErrors.contactPerson
                    }" class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors"
                        placeholder="Họ tên người liên hệ" type="text" :disabled="isLoading" />
                    <span v-if="registerErrors.contactPerson" class="text-red-500 text-xs mt-1 block">{{
                        registerErrors.contactPerson }}</span>
                </div>

                <!-- Company Email -->
                <div>
                    <label class="block text-sm font-semibold mb-1">Email công ty <span
                            class="text-red-500">*</span></label>
                    <input v-model="registerForm.email" :class="{
                        'border-red-500 dark:border-red-500': registerErrors.email,
                        'border-slate-200 dark:border-slate-700': !registerErrors.email
                    }" class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors"
                        placeholder="company@example.com" type="email" :disabled="isLoading" />
                    <span v-if="registerErrors.email" class="text-red-500 text-xs mt-1 block">{{ registerErrors.email
                        }}</span>
                </div>

                <!-- Phone -->
                <div>
                    <label class="block text-sm font-semibold mb-1">Số điện thoại <span
                            class="text-red-500">*</span></label>
                    <input v-model="registerForm.phone" :class="{
                        'border-red-500 dark:border-red-500': registerErrors.phone,
                        'border-slate-200 dark:border-slate-700': !registerErrors.phone
                    }" class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors"
                        placeholder="0901234567" type="tel" :disabled="isLoading" />
                    <span v-if="registerErrors.phone" class="text-red-500 text-xs mt-1 block">{{ registerErrors.phone
                        }}</span>
                </div>

                <!-- Password -->
                <div>
                    <label class="block text-sm font-semibold mb-1">Mật khẩu <span class="text-red-500">*</span></label>
                    <div class="relative">
                        <input v-model="registerForm.password" :type="showPassword ? 'text' : 'password'" :class="{
                            'border-red-500 dark:border-red-500': registerErrors.password,
                            'border-slate-200 dark:border-slate-700': !registerErrors.password
                        }" class="w-full rounded-lg dark:bg-slate-800 focus:ring-[#2463eb] focus:border-[#2463eb] border transition-colors pr-10"
                            placeholder="••••••••" :disabled="isLoading" />
                        <button type="button" @click="showPassword = !showPassword"
                            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
                            <span class="material-symbols-outlined text-sm">{{ showPassword ? 'visibility_off' :
                                'visibility'
                                }}</span>
                        </button>
                    </div>
                    <span v-if="registerErrors.password" class="text-red-500 text-xs mt-1 block">{{
                        registerErrors.password
                        }}</span>
                </div>

                <!-- Register Button -->
                <button type="submit" :disabled="isLoading"
                    class="w-full bg-[#2463eb] text-white font-bold py-3 rounded-lg mt-6 hover:bg-[#2463eb]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                    <span v-if="!isLoading">Đăng ký Doanh Nghiệp</span>
                    <span v-else class="flex items-center gap-2">
                        <span class="material-symbols-outlined animate-spin">hourglass_top</span>
                        Đang xử lý...
                    </span>
                </button>
            </form>

            <!-- Divider -->
            <!--<div class="mt-8">
                <div class="relative flex py-5 items-center">
                    <div class="flex-grow border-t border-slate-300 dark:border-slate-700"></div>
                    <span class="flex-shrink mx-4 text-slate-400 text-sm">Hoặc đăng ký với</span>
                    <div class="flex-grow border-t border-slate-300 dark:border-slate-700"></div>
                </div>
            </div>-->

            <!-- Social Register -->
            <!--<div class="grid grid-cols-2 gap-4">
                <button type="button" @click="handleSocialLogin('google')" :disabled="isLoading"
                    class="flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700 rounded-lg py-2 hover:bg-white dark:hover:bg-slate-700 transition-colors disabled:opacity-50">
                    <svg class="w-5 h-5" viewBox="0 0 24 24">
                        <path
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            fill="#4285F4"></path>
                        <path
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            fill="#34A853"></path>
                        <path
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                            fill="#FBBC05"></path>
                        <path
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            fill="#EA4335"></path>
                    </svg>
                    <span class="text-sm font-medium hidden sm:inline">Google</span>
                </button>
                <button type="button" @click="handleSocialLogin('facebook')" :disabled="isLoading"
                    class="flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700 rounded-lg py-2 hover:bg-white dark:hover:bg-slate-700 transition-colors disabled:opacity-50">
                    <svg class="w-5 h-5" fill="#1877F2" viewBox="0 0 24 24">
                        <path
                            d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z">
                        </path>
                    </svg>
                    <span class="text-sm font-medium hidden sm:inline">Facebook</span>
                </button>
            </div>-->
            
            <!-- Login Link -->
            <p class="text-center text-sm text-slate-600 dark:text-slate-400 mt-8">
                Đã có tài khoản?
                <router-link to="/employer/login" class="text-[#2463eb] font-semibold hover:underline">
                    Đăng nhập tại đây
                </router-link>
            </p>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'

const router = useRouter()
const isLoading = ref(false)
const showPassword = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Register form for employer
const registerForm = reactive({
    companyName: '',
    contactPerson: '',
    email: '',
    phone: '',
    password: '',
})

const registerErrors = reactive({
    companyName: '',
    contactPerson: '',
    email: '',
    phone: '',
    password: '',
})

// Validate register form
const validateRegister = () => {
    registerErrors.companyName = ''
    registerErrors.contactPerson = ''
    registerErrors.email = ''
    registerErrors.phone = ''
    registerErrors.password = ''

    if (!registerForm.companyName.trim()) {
        registerErrors.companyName = 'Vui lòng nhập tên công ty'
    }

    if (!registerForm.contactPerson.trim()) {
        registerErrors.contactPerson = 'Vui lòng nhập tên người liên hệ'
    }

    if (!registerForm.email.trim()) {
        registerErrors.email = 'Vui lòng nhập email'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
        registerErrors.email = 'Email không hợp lệ'
    }

    if (!registerForm.phone.trim()) {
        registerErrors.phone = 'Vui lòng nhập số điện thoại'
    } else if (!/^0\d{9}$/.test(registerForm.phone.replace(/\s+/g, ''))) {
        registerErrors.phone = 'Số điện thoại không hợp lệ'
    }

    if (!registerForm.password) {
        registerErrors.password = 'Vui lòng nhập mật khẩu'
    } else if (registerForm.password.length < 6) {
        registerErrors.password = 'Mật khẩu phải có ít nhất 6 ký tự'
    }

    return Object.values(registerErrors).every(err => !err)
}

// Handle register
const handleRegister = async () => {
    if (!validateRegister()) {
        return
    }

    isLoading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    try {
        const response = await authService.registerEmployer(
            registerForm.companyName,
            registerForm.contactPerson,
            registerForm.email,
            registerForm.phone,
            registerForm.password
        )

        if (response.success || response.message) {
            successMessage.value = 'Đăng ký thành công! Vui lòng đăng nhập.'
            // Reset form
            Object.assign(registerForm, {
                companyName: '',
                contactPerson: '',
                email: '',
                phone: '',
                password: '',
            })

            // Redirect to login after 2 seconds
            setTimeout(() => {
                router.push('/employer/login')
            }, 2000)
        }
    } catch (error) {
        errorMessage.value = error.message || 'Đăng ký thất bại'
    } finally {
        isLoading.value = false
    }
}

// Handle social login
const handleSocialLogin = (provider) => {
    console.log(`Register with ${provider}`)
}
</script>
