import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface AnalysisResult {
  score: number;
  keywords: string[];
  suggestions: string[];
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Simulate analysis
      setAnalyzing(true);
      setTimeout(() => {
        setAnalyzing(false);
        setResult({
          score: 75,
          keywords: ['React', 'TypeScript', 'Node.js', 'Project Management'],
          suggestions: [
            'Add more specific metrics and achievements',
            'Include relevant certifications',
            'Strengthen action verbs in job descriptions'
          ]
        });
      }, 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
            Resume ATS Analyzer
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Upload your resume to get an ATS compatibility score and improvement suggestions
          </p>

          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                id="resume"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
              />
              <label
                htmlFor="resume"
                className="cursor-pointer flex flex-col items-center"
              >
                <Upload className="w-12 h-12 text-blue-500 mb-4" />
                <span className="text-lg font-medium text-gray-700">
                  {file ? file.name : 'Drop your resume here'}
                </span>
                <span className="text-sm text-gray-500 mt-2">
                  Supports PDF, DOC, DOCX
                </span>
              </label>
            </div>
          </div>

          {analyzing && (
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-3 text-gray-700">Analyzing your resume...</span>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-semibold text-gray-800">ATS Score</h2>
                  <div className="text-4xl font-bold text-blue-500">{result.score}%</div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-500 h-2.5 rounded-full"
                    style={{ width: `${result.score}%` }}
                  ></div>
                </div>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Detected Keywords
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  Suggestions for Improvement
                </h3>
                <ul className="space-y-3">
                  {result.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 mr-2" />
                      <span className="text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;