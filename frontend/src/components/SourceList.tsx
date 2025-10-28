import React from "react";

export interface Source {
  document_id: string;
  section_id: string;
  snippet: string;
  url: string;
}

interface SourceListProps {
  sources: Source[];
}

export function SourceList({ sources }: SourceListProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="source-list">
      <h4>Sources:</h4>
      <ul>
        {sources.map((source, index) => (
          <li key={`${source.section_id}-${index}`}>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="source-link"
            >
              {source.snippet.substring(0, 100)}
              {source.snippet.length > 100 ? "..." : ""}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
