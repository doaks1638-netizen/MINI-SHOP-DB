import './CategoryChip.css';

export default function CategoryChip({ category, isActive, onClick }) {
  return (
    <button
      className={`category-chip ${isActive ? 'category-chip-active' : ''}`}
      onClick={() => onClick?.(category)}
      id={`category-chip-${category.id}`}
    >
      {category.name}
    </button>
  );
}
