import { useEffect, useRef } from 'react';
import './Modal.css';

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      dialog.showModal();
    } else {
      dialog.close();
    }
  }, [isOpen]);

  const handleBackdropClick = (e) => {
    if (e.target === dialogRef.current) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <dialog
      ref={dialogRef}
      className={`modal modal-${size}`}
      onClick={handleBackdropClick}
      onClose={onClose}
    >
      <div className="modal-content animate-scaleIn">
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button className="modal-close btn-icon btn-ghost" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </dialog>
  );
}
