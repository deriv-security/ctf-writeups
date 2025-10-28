export function requireAuth(req, res, next) {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Authentication required. Please cross the threshold first.' });
  }
  next();
}

export function optionalAuth(req, res, next) {
  // Allow both authenticated and unauthenticated access
  next();
}
