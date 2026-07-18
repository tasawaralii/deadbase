"use client";

import Image from "next/image";
import { useEffect, useReducer, useState, type FormEvent } from "react";
import { ApiError } from "@/lib/api";
import { createComment, getComments } from "@/lib/posts";
import type { CommentPublic } from "@/lib/types";
import { formatCommentDate } from "@/lib/format";

type CommentNode = CommentPublic & { children: CommentNode[] };

function buildTree(comments: CommentPublic[]): CommentNode[] {
  const byId = new Map<number, CommentNode>();
  for (const c of comments) byId.set(c.id, { ...c, children: [] });

  const roots: CommentNode[] = [];
  for (const c of comments) {
    const node = byId.get(c.id)!;
    const parent = c.parent_id !== null ? byId.get(c.parent_id) : undefined;
    if (parent) parent.children.push(node);
    else roots.push(node);
  }
  return roots;
}

function CommentForm({
  slug,
  parentId,
  onPosted,
  onCancel,
}: {
  slug: string;
  parentId: number | null;
  onPosted: (comment: CommentPublic) => void;
  onCancel?: () => void;
}) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const body = String(data.get("body") ?? "").trim();
    const authorName = String(data.get("author_name") ?? "").trim();
    const authorEmail = String(data.get("author_email") ?? "").trim();
    const authorUrl = String(data.get("author_url") ?? "").trim();

    if (!body || !authorName || !authorEmail) return;

    setSubmitting(true);
    setError(null);
    try {
      const comment = await createComment(slug, {
        body,
        author_name: authorName,
        author_email: authorEmail,
        author_url: authorUrl || null,
        parent_id: parentId,
      });
      form.reset();
      onPosted(comment);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to post comment.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-4 border border-border rounded p-4 bg-muted/30 space-y-4"
    >
      <div>
        <label className="block text-sm font-semibold mb-1">Comment</label>
        <textarea
          name="body"
          required
          maxLength={2000}
          rows={6}
          className="w-full border border-border rounded p-2 bg-white outline-none focus:border-primary"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold mb-1">Name *</label>
        <input
          name="author_name"
          required
          maxLength={50}
          className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold mb-1">Email *</label>
        <input
          name="author_email"
          type="email"
          required
          pattern="[^\s@]+@[^\s@]+\.[^\s@]+"
          title="Enter a valid email address, e.g. name@example.com"
          className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary"
        />
      </div>
      <div>
        <label className="block text-sm font-semibold mb-1">Website</label>
        <input
          name="author_url"
          className="w-full h-10 border border-border rounded px-2 bg-white outline-none focus:border-primary"
        />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={submitting}
          className="bg-accent text-accent-foreground font-bold px-6 py-3 uppercase text-sm disabled:opacity-60"
        >
          {submitting ? "Posting..." : "Post Comment"}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="text-sm font-semibold text-muted-foreground hover:text-foreground"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}

function CommentItem({
  slug,
  node,
  replyingTo,
  setReplyingTo,
  onPosted,
}: {
  slug: string;
  node: CommentNode;
  replyingTo: number | null;
  setReplyingTo: (id: number | null) => void;
  onPosted: (comment: CommentPublic) => void;
}) {
  return (
    <li>
      <div className="flex gap-4">
        <Image
          src={node.avatar_url}
          alt={node.author_name}
          width={56}
          height={56}
          className="w-14 h-14 rounded-full shrink-0"
        />
        <div className="flex-1">
          <div className="font-display font-bold">{node.author_name}</div>
          <div className="text-xs text-muted-foreground mb-2">
            {formatCommentDate(node.created_at)}
          </div>
          <p className="text-sm">{node.body}</p>
          <button
            onClick={() => setReplyingTo(replyingTo === node.id ? null : node.id)}
            className="mt-2 text-xs font-bold uppercase text-accent hover:underline"
          >
            Reply
          </button>
        </div>
      </div>

      {replyingTo === node.id && (
        <div className="ml-14 mt-3">
          <CommentForm
            slug={slug}
            parentId={node.id}
            onPosted={(c) => {
              onPosted(c);
              setReplyingTo(null);
            }}
            onCancel={() => setReplyingTo(null)}
          />
        </div>
      )}

      {node.children.length > 0 && (
        <ul className="mt-6 ml-8 md:ml-14 pl-4 md:pl-6 border-l border-border space-y-6">
          {node.children.map((child) => (
            <CommentItem
              key={child.id}
              slug={slug}
              node={child}
              replyingTo={replyingTo}
              setReplyingTo={setReplyingTo}
              onPosted={onPosted}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

const PAGE_SIZE = 10;

type CommentsState = {
  comments: CommentPublic[];
  totalCount: number | null;
  rootCount: number;
  page: number;
  loading: boolean;
  loadingMore: boolean;
  loadError: string | null;
};

type CommentsAction =
  | { type: "load_start"; isFirst: boolean }
  | {
      type: "load_success";
      isFirst: boolean;
      page: number;
      data: CommentPublic[];
      totalCount: number;
      rootCount: number;
    }
  | { type: "load_error"; isFirst: boolean; message: string }
  | { type: "comment_posted"; comment: CommentPublic };

const initialCommentsState: CommentsState = {
  comments: [],
  totalCount: null,
  rootCount: 0,
  page: 0,
  loading: true,
  loadingMore: false,
  loadError: null,
};

function commentsReducer(state: CommentsState, action: CommentsAction): CommentsState {
  switch (action.type) {
    case "load_start":
      return action.isFirst ? state : { ...state, loadingMore: true };
    case "load_success":
      return {
        ...state,
        comments: action.isFirst ? action.data : [...state.comments, ...action.data],
        totalCount: action.totalCount,
        rootCount: action.rootCount,
        page: action.page,
        loading: false,
        loadingMore: false,
        loadError: null,
      };
    case "load_error":
      return { ...state, loading: false, loadingMore: false, loadError: action.message };
    case "comment_posted": {
      const isRoot = action.comment.parent_id === null;
      return {
        ...state,
        // Roots are newest-first, so a brand new thread goes at the front;
        // replies stay oldest-first within their thread, so they go at the
        // back (buildTree only cares about order within a parent_id group).
        comments: isRoot
          ? [action.comment, ...state.comments]
          : [...state.comments, action.comment],
        totalCount: (state.totalCount ?? 0) + 1,
        rootCount: isRoot ? state.rootCount + 1 : state.rootCount,
      };
    }
    default:
      return state;
  }
}

export function CommentsSection({ slug }: { slug: string }) {
  const [state, dispatch] = useReducer(commentsReducer, initialCommentsState);
  const [showForm, setShowForm] = useState(false);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);

  async function loadPage(nextPage: number) {
    const isFirst = nextPage === 1;
    dispatch({ type: "load_start", isFirst });
    try {
      const res = await getComments(slug, { page: nextPage, limit: PAGE_SIZE });
      dispatch({
        type: "load_success",
        isFirst,
        page: nextPage,
        data: res.data,
        totalCount: res.total_count,
        rootCount: res.root_count,
      });
    } catch (err) {
      dispatch({
        type: "load_error",
        isFirst,
        message: err instanceof ApiError ? err.message : "Failed to load comments.",
      });
    }
  }

  useEffect(() => {
    loadPage(1);
    // Only re-fetch when the post itself changes, not on every re-render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const { comments, totalCount, rootCount, page, loading, loadingMore, loadError } = state;
  const tree = buildTree(comments);
  const hasMore = tree.length < rootCount;

  function handlePosted(comment: CommentPublic) {
    dispatch({ type: "comment_posted", comment });
  }

  return (
    <section>
      <h2 className="bg-muted inline-block px-3 py-1.5 font-display font-semibold text-sm border-b-2 border-primary">
        {totalCount ?? "…"} Comments
      </h2>

      {!showForm ? (
        <button
          onClick={() => setShowForm(true)}
          className="mt-4 w-full text-left border border-border rounded p-4 text-muted-foreground italic hover:border-primary transition-colors"
        >
          Click here to post a comment
        </button>
      ) : (
        <CommentForm
          slug={slug}
          parentId={null}
          onPosted={(c) => {
            handlePosted(c);
            setShowForm(false);
          }}
        />
      )}

      {loading ? (
        <p className="mt-8 text-sm text-muted-foreground">Loading comments...</p>
      ) : loadError ? (
        <p className="mt-8 text-sm text-destructive">{loadError}</p>
      ) : (
        <>
          <ul className="mt-8 space-y-6 divide-y divide-border [&>li]:pt-6 first:[&>li]:pt-0">
            {tree.map((node) => (
              <CommentItem
                key={node.id}
                slug={slug}
                node={node}
                replyingTo={replyingTo}
                setReplyingTo={setReplyingTo}
                onPosted={handlePosted}
              />
            ))}
          </ul>

          {hasMore && (
            <button
              onClick={() => loadPage(page + 1)}
              disabled={loadingMore}
              className="mt-6 w-full border border-border rounded p-3 text-sm font-semibold hover:border-primary transition-colors disabled:opacity-60"
            >
              {loadingMore ? "Loading..." : "Load more comments"}
            </button>
          )}
        </>
      )}
    </section>
  );
}
