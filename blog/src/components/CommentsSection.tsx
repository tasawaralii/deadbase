"use client";

import { useState } from "react";

// Placeholder until wired to GET/POST /api/v1/public/posts/{slug}/comments
const COMMENTS = [
  { name: "Ark", date: "March 18, 2024 at 5:56 pm", text: "Thanks for the post!" },
  { name: "Shdyhd", date: "April 1, 2025 at 12:34 pm", text: "Nice release — looking forward to more." },
];

export function CommentsSection() {
  const [showForm, setShowForm] = useState(false);

  return (
    <section>
      <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary">
        {COMMENTS.length} Comments
      </h2>

      {!showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="mt-4 w-full text-left border border-border rounded p-4 text-muted-foreground italic hover:border-primary transition-colors"
        >
          Click here to post a comment
        </button>
      ) : (
        <form className="mt-4 border border-border rounded p-4 bg-muted/30 space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div>
            <label className="block text-sm font-semibold mb-1">Comment</label>
            <textarea rows={6} className="w-full border border-border rounded p-2 bg-white outline-none focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Name *</label>
            <input className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Email *</label>
            <input type="email" className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-semibold mb-1">Website</label>
            <input className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary" />
          </div>
          <button type="submit" className="bg-accent text-accent-foreground font-bold px-6 py-3 uppercase text-sm w-full sm:w-auto">
            Post Comment
          </button>
        </form>
      )}

      <ul className="mt-8 space-y-6">
        {COMMENTS.map((c, i) => (
          <li key={i} className="flex gap-4 border-b border-border pb-6">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-accent shrink-0" />
            <div className="flex-1">
              <div className="font-display font-bold">{c.name}</div>
              <div className="text-xs text-muted-foreground mb-2">{c.date}</div>
              <p className="text-sm">{c.text}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
