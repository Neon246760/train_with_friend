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

// 添加响应拦截器，处理 401 错误
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            // 简单直接地跳转到登录页，并刷新以清除可能存在的旧状态
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
