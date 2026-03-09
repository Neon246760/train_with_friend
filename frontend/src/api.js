import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // 使用相对路径，配合 Nginx 或 Vite 代理
});

// 添加拦截器，自动添加 token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default api;
