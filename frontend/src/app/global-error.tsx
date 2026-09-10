"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body>
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-8 text-center space-y-4">
          <h2 className="text-3xl font-bold text-red-500">Critical System Error</h2>
          <p className="text-gray-400">The application encountered a fatal error.</p>
          <button
            onClick={() => reset()}
            className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors"
          >
            Restart Application
          </button>
        </div>
      </body>
    </html>
  );
}
