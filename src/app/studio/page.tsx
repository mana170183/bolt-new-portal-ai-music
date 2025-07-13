import AdvancedMusicGenerator from '@/components/AdvancedMusicGenerator';

export default async function StudioPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Music Studio
          </h1>
          <p className="text-lg text-gray-600">
            Advanced AI music generation with full creative control
          </p>
        </div>
        
        <AdvancedMusicGenerator />
      </div>
    </div>
  );
}
