import React from "react";
import { Composition } from "remotion";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";

export const Root: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="BridgeShortHalf" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={540} height={960} />
    <Composition id="BridgeShortTiny" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={360} height={640} />
  </>
);
