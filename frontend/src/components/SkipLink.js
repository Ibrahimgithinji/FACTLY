import { useSkipLink } from '../hooks/useAccessibility';

export default function SkipLink() {
  useSkipLink('main-content');
  return null;
}
