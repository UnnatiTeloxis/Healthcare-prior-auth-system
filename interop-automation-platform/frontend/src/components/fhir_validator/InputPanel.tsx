import { useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setCurrentResource } from '../../store/fhirValidatorSlice';
import { RootState } from '../../store';

export default function InputPanel() {
  const dispatch = useDispatch();
  const currentResource = useSelector((state: RootState) => state.fhirValidator.currentResource);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleResourceChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    dispatch(setCurrentResource(e.target.value));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result as string;
        dispatch(setCurrentResource(content));
      };
      reader.readAsText(file);
    }
  };

  const handleClear = () => {
    dispatch(setCurrentResource(''));
    setFileName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleLoadExample = () => {
    const examplePatient = {
      resourceType: "Patient",
      id: "example",
      text: {
        status: "generated",
        div: "<div xmlns=\"http://www.w3.org/1999/xhtml\">Patient Example</div>"
      },
      identifier: [
        {
          system: "http://example.org/mrn",
          value: "12345"
        }
      ],
      name: [
        {
          use: "official",
          family: "Doe",
          given: ["John"]
        }
      ],
      gender: "male",
      birthDate: "1974-12-25"
    };
    dispatch(setCurrentResource(JSON.stringify(examplePatient, null, 2)));
    setFileName('');
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">FHIR Resource Input</h2>
        <div className="flex gap-2">
          <button
            onClick={handleLoadExample}
            className="px-3 py-1 text-sm bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
          >
            Load Example
          </button>
          <button
            onClick={handleClear}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="mb-4">
        <label className="flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded border border-gray-300 cursor-pointer hover:bg-gray-100">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <span>Upload JSON/XML File</span>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.xml"
            onChange={handleFileUpload}
            className="hidden"
          />
        </label>
        {fileName && (
          <p className="mt-2 text-sm text-gray-600">
            Loaded: <span className="font-medium">{fileName}</span>
          </p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Paste FHIR Resource (JSON or XML)
        </label>
        <textarea
          value={currentResource}
          onChange={handleResourceChange}
          placeholder='Paste your FHIR resource here or upload a file...'
          className="w-full h-96 p-3 font-mono text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          spellCheck={false}
        />
        <div className="mt-2 flex justify-between text-xs text-gray-500">
          <span>Supports JSON and XML formats</span>
          <span>{currentResource.length} characters</span>
        </div>
      </div>
    </div>
  );
}
