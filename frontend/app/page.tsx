export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          歡迎使用問卷系統
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          快速建立、分發和分析您的問卷調查
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">建立問卷</h3>
            <p className="text-gray-600">
              使用直覺的介面快速建立多種類型的問卷
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">數據分析</h3>
            <p className="text-gray-600">
              即時查看回覆統計和視覺化圖表
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-blue-600 text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-semibold mb-2">快速分發</h3>
            <p className="text-gray-600">
              輕鬆分享問卷連結，收集更多回覆
            </p>
          </div>
        </div>
        
        <div className="mt-12">
          <a
            href="/surveys/create"
            className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-blue-700 transition-colors"
          >
            開始建立問卷
          </a>
        </div>
      </div>
    </div>
  );
}