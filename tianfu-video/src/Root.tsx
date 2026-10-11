import React from "react";
import { Composition } from "remotion";
import { StockVideo } from "./Video";
import { CoverA, CoverB } from "./Cover";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Stock"
        component={StockVideo}
        durationInFrames={2760}
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition id="CoverA" component={CoverA} durationInFrames={1} fps={30} width={1080} height={1920} />
      <Composition id="CoverB" component={CoverB} durationInFrames={1} fps={30} width={1080} height={1920} />
    </>
  );
};