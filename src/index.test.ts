import { describe, expect, it } from "vitest";
import entry, { isOwnerSession } from "./index.js";
import { getToolPluginMetadata } from "openclaw/plugin-sdk/tool-plugin";
const scope = {agentId:"main",allowedSessionKeys:["agent:main:telegram:direct:123", "agent:main:main"],reflectionSessionPrefixes:["agent:main:cron:owner-review"]};
describe("sidecar scope", () => {
  it("declares the four bounded tools", () => {
    expect(getToolPluginMetadata(entry)?.tools.map(t => t.name)).toEqual(["hyperspace_lab_status","hyperspace_lab_search","hyperspace_lab_store","hyperspace_lab_cognitive"]);
  });
  it("defaults to no owner sessions and opt-in recall", () => {
    const p = getToolPluginMetadata(entry)!.configSchema.properties as any;
    expect(p.allowedSessionKeys.default).toEqual([]);
    expect(p.prefetchEnabled.default).toBe(false);
    expect(p.allowInsecureRemote.default).toBe(false);
  });
  it("allows exact owner and boundary-delimited reflection children", () => {
    for(const sessionKey of [...scope.allowedSessionKeys,"agent:main:cron:owner-review","agent:main:cron:owner-review:run:123"])
      expect(isOwnerSession({agentId:"main",sessionKey},scope)).toBe(true);
  });
  it("rejects unknown agents, missing keys, prefix collisions, groups even when allowlisted", () => {
    for(const sessionKey of [undefined,"agent:main:cron:owner-review-evil","agent:main:telegram:direct:1234"])
      expect(isOwnerSession({agentId:"main",sessionKey},scope)).toBe(false);
    expect(isOwnerSession({agentId:"other",sessionKey:"agent:main:main"},scope)).toBe(false);
    const key="agent:main:telegram:group:123";
    expect(isOwnerSession({agentId:"main",sessionKey:key},{...scope,allowedSessionKeys:[key]})).toBe(false);
  });
});
