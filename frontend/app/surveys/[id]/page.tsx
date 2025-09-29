'use client';

import { useEffect, useState } from 'react';
import { surveyApi, responseApi } from '@/lib/api';
import { Survey, Answer } from '@/types';
import { useRouter } from 'next/navigation';

export default function SurveyDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [survey, setSurvey] = useState<Survey | null>(null);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadSurvey();
  }, [params.id]);

  const loadSurvey = async () => {
    try {
      const response = await surveyApi.getById(parseInt(params.id));
      setSurvey(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '載入問卷失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId: number, value: any) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      const answersArray = Object.entries(answers).map(([questionId, value]) => ({
        question_id: parseInt(questionId),
        answer_text: typeof value === 'string' ? value : null,
        answer_data: typeof value !== 'string' ? value : null,
      }));

      await responseApi.submit(parseInt(params.id), {
        answers: answersArray,
      });

      setSuccess(true);
      setTimeout(() => {
        router.push('/surveys');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || '提交失敗');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center">載入中...</div>
      </div>
    );
  }

  if (!survey) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center text-red-600">找不到問卷</div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <div className="text-green-600 text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-green-900 mb-2">提交成功！</h2>
          <p className="text-green-700">感謝您的填寫，即將返回問卷列表...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-lg shadow-md p-8 mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{survey.title}</h1>
        {survey.description && (
          <p className="text-gray-600 mb-6">{survey.description}</p>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {survey.questions?.map((question, index) => (
          <div key={question.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="mb-4">
              <label className="block text-lg font-medium text-gray-900 mb-2">
                {index + 1}. {question.question_text}
                {question.is_required && (
                  <span className="text-red-500 ml-1">*</span>
                )}
              </label>
            </div>

            {question.question_type === 'text' && (
              <textarea
                value={answers[question.id] || ''}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                required={question.is_required}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="請輸入您的答案"
              />
            )}

            {question.question_type === 'radio' && (
              <div className="space-y-2">
                {question.options?.map((option, optIndex) => (
                  <label key={optIndex} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={option}
                      checked={answers[question.id] === option}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      required={question.is_required}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            )}

            {question.question_type === 'checkbox' && (
              <div className="space-y-2">
                {question.options?.map((option, optIndex) => (
                  <label key={optIndex} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      value={option}
                      checked={answers[question.id]?.includes(option)}
                      onChange={(e) => {
                        const current = answers[question.id] || [];
                        const newValue = e.target.checked
                          ? [...current, option]
                          : current.filter((v: string) => v !== option);
                        handleAnswerChange(question.id, newValue);
                      }}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            )}

            {question.question_type === 'rating' && (
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    type="button"
                    onClick={() => handleAnswerChange(question.id, rating)}
                    className={`w-12 h-12 rounded-full border-2 ${
                      answers[question.id] === rating
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                    }`}
                  >
                    {rating}
                  </button>
                ))}
              </div>
            )}

            {question.question_type === 'dropdown' && (
              <select
                value={answers[question.id] || ''}
                onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                required={question.is_required}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">請選擇...</option>
                {question.options?.map((option, optIndex) => (
                  <option key={optIndex} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            )}
          </div>
        ))}

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {submitting ? '提交中...' : '提交問卷'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            返回
          </button>
        </div>
      </form>
    </div>
  );
}