export default function Pagination({ page, onPageChange, hasMore }) {
  return (
    <div className="pagination">
      <button
        className="pagination-btn"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
      >
        ‹
      </button>

      {page > 1 && (
        <button className="pagination-btn" onClick={() => onPageChange(1)}>1</button>
      )}

      {page > 2 && <span className="pagination-dots">…</span>}

      <button className="pagination-btn active">{page}</button>

      {hasMore && (
        <button className="pagination-btn" onClick={() => onPageChange(page + 1)}>{page + 1}</button>
      )}

      <button
        className="pagination-btn"
        onClick={() => onPageChange(page + 1)}
        disabled={!hasMore}
      >
        ›
      </button>
    </div>
  );
}
