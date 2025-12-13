/**
 * Workplan Upload Page
 *
 * Allows admins to upload SAFMC workplan Excel files.
 * Parses the file and imports items, milestones, and metadata into the database.
 */

import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2, X } from 'lucide-react';

const WorkplanUpload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [versionName, setVersionName] = useState('');
  const [quarter, setQuarter] = useState('');
  const [fiscalYear, setFiscalYear] = useState(new Date().getFullYear());
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  // Handle file selection
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xlsx')) {
        setError('Please select an Excel file (.xlsx)');
        return;
      }
      setFile(selectedFile);
      setError(null);

      // Auto-populate version name from filename if not set
      if (!versionName) {
        const name = selectedFile.name.replace('.xlsx', '').replace(/_/g, ' ');
        setVersionName(name);
      }
    }
  };

  // Handle drag and drop
  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (!droppedFile.name.endsWith('.xlsx')) {
        setError('Please drop an Excel file (.xlsx)');
        return;
      }
      setFile(droppedFile);
      setError(null);

      // Auto-populate version name from filename if not set
      if (!versionName) {
        const name = droppedFile.name.replace('.xlsx', '').replace(/_/g, ' ');
        setVersionName(name);
      }
    }
  }, [versionName]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!versionName) {
      setError('Please enter a version name');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('version_name', versionName);
      if (quarter) formData.append('quarter', quarter);
      if (fiscalYear) formData.append('fiscal_year', fiscalYear);

      const response = await fetch('/api/workplan/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      setUploadResult(data);

      // Clear form
      setFile(null);
      setVersionName('');
      setQuarter('');

      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';

    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Clear file selection
  const clearFile = () => {
    setFile(null);
    setError(null);
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Upload Workplan
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Upload SAFMC workplan Excel files to import amendments, milestones, and tracking data.
        </p>
      </div>

      {/* Success Message */}
      {uploadResult && (
        <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-green-900 dark:text-green-100 mb-1">
                Upload Successful!
              </h3>
              <p className="text-sm text-green-800 dark:text-green-200 mb-2">
                Workplan "{uploadResult.version?.version_name}" has been imported.
              </p>
              <div className="text-sm text-green-700 dark:text-green-300 space-y-1">
                <p>Items created: {uploadResult.stats?.itemsCreated}</p>
                <p>Milestones created: {uploadResult.stats?.milestonesCreated}</p>
                <p>Processing time: {uploadResult.stats?.processingTimeMs}ms</p>
              </div>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => navigate('/workplan')}
                  className="text-sm font-medium text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 underline"
                >
                  View Workplan
                </button>
                <button
                  onClick={() => setUploadResult(null)}
                  className="text-sm font-medium text-green-700 dark:text-green-300 hover:text-green-800 dark:hover:text-green-200 underline"
                >
                  Upload Another
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-red-900 dark:text-red-100 mb-1">
                Upload Failed
              </h3>
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Upload Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload Area */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Excel File
          </label>

          {/* Drag and Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging
                ? 'border-brand-blue bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            <input
              id="file-input"
              type="file"
              accept=".xlsx"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isUploading}
            />

            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileSpreadsheet className="w-8 h-8 text-green-600 dark:text-green-400" />
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button
                  type="button"
                  onClick={clearFile}
                  className="ml-2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  disabled={isUploading}
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Drop your Excel file here, or click to browse
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500">
                  Supports .xlsx files
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata Fields */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Version Name */}
          <div className="md:col-span-2">
            <label htmlFor="version-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Version Name *
            </label>
            <input
              id="version-name"
              type="text"
              value={versionName}
              onChange={(e) => setVersionName(e.target.value)}
              placeholder="e.g., Q3 2025 Workplan"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              required
              disabled={isUploading}
            />
          </div>

          {/* Fiscal Year */}
          <div>
            <label htmlFor="fiscal-year" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Fiscal Year
            </label>
            <input
              id="fiscal-year"
              type="number"
              value={fiscalYear}
              onChange={(e) => setFiscalYear(parseInt(e.target.value))}
              min="2020"
              max="2030"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              disabled={isUploading}
            />
          </div>
        </div>

        {/* Quarter (Optional) */}
        <div>
          <label htmlFor="quarter" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Quarter (Optional)
          </label>
          <select
            id="quarter"
            value={quarter}
            onChange={(e) => setQuarter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
            disabled={isUploading}
          >
            <option value="">Select quarter...</option>
            <option value="Q1">Q1 (Dec-Feb)</option>
            <option value="Q2">Q2 (Mar-May)</option>
            <option value="Q3">Q3 (Jun-Aug)</option>
            <option value="Q4">Q4 (Sep-Nov)</option>
          </select>
        </div>

        {/* Submit Button */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!file || !versionName || isUploading}
            className="px-6 py-2.5 bg-brand-blue text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isUploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Upload Workplan
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => navigate('/workplan')}
            className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            disabled={isUploading}
          >
            Cancel
          </button>
        </div>
      </form>

      {/* Help Text */}
      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
        <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
          File Format Requirements
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
          <li>File must be in Excel format (.xlsx)</li>
          <li>Should contain columns: Amendment #, Topic, SAFMC Lead</li>
          <li>Quarterly milestones should be in date columns (Dec-25, Mar-26, etc.)</li>
          <li>Supports both 2023 and 2025+ workplan formats</li>
          <li>Category sections (UNDERWAY, PLANNED, OTHER) are automatically detected</li>
        </ul>
      </div>
    </div>
  );
};

export default WorkplanUpload;
