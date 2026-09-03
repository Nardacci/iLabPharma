/*
 * Compatibility loader.
 * The canonical Módulo Principal flow is rendered by journey-flow.js.
 * This file intentionally does not redefine renderStageFlow, preventing
 * the legacy renderer from replacing the current journey layout.
 */
(function(){
  if(typeof window.renderStageFlow!=='function') return;
})();
