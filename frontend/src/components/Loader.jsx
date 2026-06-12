import './Loader.css';

export default function Loader({ size = 'md', text }) {
  return (
    <div className={`loader-wrapper loader-${size}`}>
      <div className="loader-spinner">
        <div className="loader-ring"></div>
        <div className="loader-ring"></div>
        <div className="loader-ring"></div>
      </div>
      {text && <p className="loader-text">{text}</p>}
    </div>
  );
}
