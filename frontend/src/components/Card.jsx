function Card({ children, className = '', title, subtitle, actions }) {
  return (
    <div className={`card ${className}`}>
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-6">
          <div>
            {title && <h3 className="text-xl font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center space-x-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  )
}

export default Card

