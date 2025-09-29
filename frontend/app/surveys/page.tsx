'use client';

import { useEffect, useState } from 'react';
import { surveyApi } from '@/lib/api';
import { Survey } from '@/types';
import Link from 'next/link';

export default function SurveysPage() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSurveys();
  }, []);

  const loadSurveys = async () => {
    try {
      const response = await surveyApi.getAll();
      setSurveys(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '載入問卷失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('確定要刪除此問卷嗎？')) return;
    
    try {
      await surveyApi.delete(id);
      setSurveys(surveys.filter(s => s.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || '刪除失敗');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center">載入中...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">問卷列表</h1>
        <Link
          href="/surveys/create"
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          建立新問卷
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {surveys.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-600 mb-4">目前沒有問卷</p>
          <Link
            href="/surveys/create"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            建立第一個問卷
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {surveys.map((survey) => (
            <div
              key={survey.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold text-gray-900">
                  {survey.title}
                </h3>
                <span
                  className={`px-2 py-1 text-xs rounded ${
                    survey.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {survey.is_active ? '進行中' : '已結束'}
                </span>
              </div>
              
              {survey.description && (
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {survey.description}
                </p>
              )}
              
              <div className="text-sm text-gray-500 mb-4">
                建立時間: {new Date(survey.created_at).toLocaleDateString('zh-TW')}
              </div>
              
              <div className="flex space-x-2">
                <Link
                  href={`/surveys/${survey.id}`}
                  className="flex-1 text-center bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  查看
                </Link>
                <Link
                  href={`/surveys/${survey.id}/statistics`}
                  className="flex-1 text-center bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
                >
                  統計
                </Link>
                <button
                  onClick={() => handleDelete(survey.id)}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  刪除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}