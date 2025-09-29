import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Survey API
export const surveyApi = {
  getAll: () => api.get('/surveys'),
  getById: (id: number) => api.get(`/surveys/${id}`),
  create: (data: any) => api.post('/surveys', data),
  update: (id: number, data: any) => api.put(`/surveys/${id}`, data),
  delete: (id: number) => api.delete(`/surveys/${id}`),
  getStatistics: (id: number) => api.get(`/surveys/${id}/statistics`),
};

// Response API
export const responseApi = {
  submit: (surveyId: number, data: any) => api.post(`/surveys/${surveyId}/responses`, data),
  getAll: (surveyId: number) => api.get(`/surveys/${surveyId}/responses`),
  getById: (surveyId: number, responseId: number) => 
    api.get(`/surveys/${surveyId}/responses/${responseId}`),
};

// Question API
export const questionApi = {
  create: (surveyId: number, data: any) => api.post(`/surveys/${surveyId}/questions`, data),
  update: (surveyId: number, questionId: number, data: any) => 
    api.put(`/surveys/${surveyId}/questions/${questionId}`, data),
  delete: (surveyId: number, questionId: number) => 
    api.delete(`/surveys/${surveyId}/questions/${questionId}`),
};

export default api;