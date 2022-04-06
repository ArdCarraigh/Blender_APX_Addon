template_hairworks = '''<!DOCTYPE NvParameters>
<NvParameters numObjects="4" version="1.0" >
<value name="" type="Ref" className="HairWorksInfo" version="1.1" checksum="">
    <struct name="">
        <value name="fileVersion" type="String">1.1</value>
        <value name="toolVersion" type="String"></value>
        <value name="sourcePath" type="String"></value>
        <value name="authorName" type="String"></value>
        <value name="lastModified" type="String"></value>
    </struct>
</value>
<value name="" type="Ref" className="HairSceneDescriptor" version="1.1" checksum="">
    <struct name="">
        <value name="densityTexture" type="String"></value>
        <value name="rootColorTexture" type="String"></value>
        <value name="tipColorTexture" type="String"></value>
        <value name="widthTexture" type="String"></value>
        <value name="rootWidthTexture" null="1" type="String"></value>
        <value name="tipWidthTexture" null="1" type="String"></value>
        <value name="stiffnessTexture" type="String"></value>
        <value name="rootStiffnessTexture" type="String"></value>
        <value name="clumpScaleTexture" type="String"></value>
        <value name="clumpRoundnessTexture" type="String"></value>
        <value name="clumpNoiseTexture" null="1" type="String"></value>
        <value name="waveScaletexture" type="String"></value>
        <value name="waveFreqTexture" type="String"></value>
        <value name="strandTexture" type="String"></value>
        <value name="lengthTexture" type="String"></value>
        <value name="specularTexture" type="String"></value>
    </struct>
</value>
<value name="" type="Ref" className="HairAssetDescriptor" version="1.1" checksum="">
    <struct name="">
        <value name="numGuideHairs" type="U32">{numHairs}</value>
        <value name="numVertices" type="U32">{totalVerts}</value>
        <array name="vertices" size="{totalVerts}" type="Vec3">
            {hair_verts}
        </array>
        <array name="endIndices" size="{numHairs}" type="U32">
            {endIndices}
        </array>
        <value name="numFaces" type="U32">{numFaces}</value>
        <array name="faceIndices" size="{n_faceIndices}" type="U32">
            {faceIndices} 
        </array>
        <array name="faceUVs" size="{n_UVs}" type="Vec2">
            {UVs}
        </array>
        <value name="numBones" type="U32">{numBones}</value>
        <array name="boneIndices" size="{numHairs}" type="Vec4">
            {boneIndices}
        </array>
        <array name="boneWeights" size="{numHairs}" type="Vec4">
            {boneWeights}
        </array>
        <array name="boneNames" size="{boneNamesSize}" type="U8">
            {boneNames}
        </array>
        <array name="boneNameList" size="{numBones}" type="String">
            {boneNameList}
        </array>
        <array name="bindPoses" size="{numBones}" type="Mat44">
            {bindPoses}
        </array>
        <array name="boneParents" size="{num_boneParents}" type="I32">
            {boneParents}
        </array>
        <value name="numBoneSpheres" type="U32">{numBonesSpheres}</value>
        <array name="boneSpheres" size="{numBonesSpheres}" type="Struct" structElements="boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3)">
            {boneSpheres}
        </array>
        <value name="numBoneCapsules" type="U32">{numBoneCapsules}</value>
        <array name="boneCapsuleIndices" size="{numBoneCapsuleIndices}" type="U32">
            {boneCapsuleIndices}
        </array>
        <value name="numPinConstraints" type="U32">{numPinConstraints}</value>
        <array name="pinConstraints" size="{numPinConstraints}" type="Struct" structElements="boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3)">
            {pinConstraints}
        </array>
        <value name="sceneUnit" type="F32">1</value>
        <value name="upAxis" type="U32">1</value>
        <value name="handedness" type="U32">1</value>
    </struct>
</value>
<value name="" type="Ref" className="HairInstanceDescriptor" version="1.1" checksum="">
  <struct name="">
    <array name="materials" size="1" type="Struct">
      <struct>
        <value name="name" null="1" type="String"></value>
        <value name="densityTextureChan" type="U32">0</value>
        <value name="widthTextureChan" type="U32">0</value>
        <value name="rootWidthTextureChan" type="U32">0</value>
        <value name="tipWidthTextureChan" type="U32">0</value>
        <value name="clumpScaleTextureChan" type="U32">0</value>
        <value name="clumpNoiseTextureChan" type="U32">0</value>
        <value name="clumpRoundnessTextureChan" type="U32">0</value>
        <value name="waveScaleTextureChan" type="U32">0</value>
        <value name="waveFreqTextureChan" type="U32">0</value>
        <value name="lengthTextureChan" type="U32">0</value>
        <value name="stiffnessTextureChan" type="U32">0</value>
        <value name="rootStiffnessTextureChan" type="U32">0</value>
        <value name="splineMultiplier" type="U32">{splines}</value>
        <value name="assetType" type="U32">0</value>
        <value name="assetPriority" type="U32">0</value>
        <value name="assetGroup" type="U32">0</value>
        <value name="width" type="F32">1</value>
        <value name="widthNoise" type="F32">0</value>
        <value name="clumpNoise" type="F32">0</value>
        <value name="clumpNumSubclumps" type="U32">0</value>
        <value name="clumpRoundness" type="F32">1</value>
        <value name="clumpScale" type="F32">0</value>
        <value name="clumpPerVertex" type="Bool">false</value>
        <value name="density" type="F32">1</value>
        <value name="lengthNoise" type="F32">1</value>
        <value name="lengthScale" type="F32">1</value>
        <value name="widthRootScale" type="F32">1</value>
        <value name="widthTipScale" type="F32">0.100000001</value>
        <value name="waveRootStraighten" type="F32">0</value>
        <value name="waveScale" type="F32">0</value>
        <value name="waveScaleNoise" type="F32">0.5</value>
        <value name="waveFreq" type="F32">3</value>
        <value name="waveFreqNoise" type="F32">0.5</value>
        <value name="waveScaleStrand" type="F32">1</value>
        <value name="waveScaleClump" type="F32">0</value>
        <value name="enableDistanceLOD" type="Bool">true</value>
        <value name="distanceLODStart" type="F32">5</value>
        <value name="distanceLODEnd" type="F32">10</value>
        <value name="distanceLODFadeStart" type="F32">1000</value>
        <value name="distanceLODDensity" type="F32">0</value>
        <value name="distanceLODWidth" type="F32">1</value>
        <value name="enableDetailLOD" type="Bool">true</value>
        <value name="detailLODStart" type="F32">2</value>
        <value name="detailLODEnd" type="F32">1</value>
        <value name="detailLODDensity" type="F32">1</value>
        <value name="detailLODWidth" type="F32">1</value>
        <value name="colorizeLODOption" type="U32">0</value>
        <value name="useViewfrustrumCulling" type="Bool">true</value>
        <value name="useBackfaceCulling" type="Bool">false</value>
        <value name="backfaceCullingThreshold" type="F32">-0.200000003</value>
        <value name="usePixelDensity" type="Bool">false</value>
        <value name="alpha" type="F32">0</value>
        <value name="strandBlendScale" type="F32">1</value>
        <value name="baseColor" type="Vec4">0 0 0 0</value>
        <value name="diffuseBlend" type="F32">0.5</value>
        <value name="diffuseScale" type="F32">0</value>
        <value name="diffuseHairNormalWeight" type="F32">0</value>
        <value name="diffuseBoneIndex" type="U32">0</value>
        <value name="diffuseBoneLocalPos" type="Vec3">0 0 0</value>
        <value name="diffuseNoiseFreqU" type="F32">0</value>
        <value name="diffuseNoiseFreqV" type="F32">0</value>
        <value name="diffuseNoiseScale" type="F32">0</value>
        <value name="diffuseNoiseGain" type="F32">0</value>
        <value name="textureBrightness" type="F32">0</value>
        <value name="diffuseColor" type="Vec4">0 0 0 0</value>
        <value name="rootColor" type="Vec4">1 1 1 1</value>
        <value name="tipColor" type="Vec4">1 1 1 1</value>
        <value name="glintStrength" type="F32">0</value>
        <value name="glintCount" type="F32">256</value>
        <value name="glintExponent" type="F32">2</value>
        <value name="rootAlphaFalloff" type="F32">0</value>
        <value name="rootTipColorWeight" type="F32">0.5</value>
        <value name="rootTipColorFalloff" type="F32">1</value>
        <value name="shadowSigma" type="F32">0.200000003</value>
        <value name="specularColor" type="Vec4">1 1 1 1</value>
        <value name="specularPrimary" type="F32">0.100000001</value>
        <value name="specularNoiseScale" type="F32">0</value>
        <value name="specularEnvScale" type="F32">0.25</value>
        <value name="specularPrimaryBreakup" type="F32">0</value>
        <value name="specularSecondary" type="F32">0.0500000007</value>
        <value name="specularSecondaryOffset" type="F32">0.100000001</value>
        <value name="specularPowerPrimary" type="F32">100</value>
        <value name="specularPowerSecondary" type="F32">20</value>
        <value name="strandBlendMode" type="U32">0</value>
        <value name="useTextures" type="Bool">false</value>
        <value name="useShadows" type="Bool">false</value>
        <value name="shadowDensityScale" type="F32">0.5</value>
        <value name="castShadows" type="Bool">true</value>
        <value name="receiveShadows" type="Bool">true</value>
        <value name="backStopRadius" type="F32">0</value>
        <value name="bendStiffness" type="F32">0</value>
        <value name="interactionStiffness" type="F32">0</value>
        <value name="pinStiffness" type="F32">1</value>
        <value name="collisionOffset" type="F32">0</value>
        <value name="useCollision" type="Bool">false</value>
        <value name="useDynamicPin" type="Bool">false</value>
        <value name="damping" type="F32">0</value>
        <value name="friction" type="F32">0</value>
        <value name="massScale" type="F32">10</value>
        <value name="gravity" type="Vec3">0 0 -1</value>
        <value name="inertiaScale" type="F32">1</value>
        <value name="inertiaLimit" type="F32">1000</value>
        <value name="rootStiffness" type="F32">0.5</value>
        <value name="tipStiffness" type="F32">0</value>
        <value name="simulate" type="Bool">true</value>
        <value name="stiffness" type="F32">0.5</value>
        <value name="stiffnessStrength" type="F32">1</value>
        <value name="stiffnessDamping" type="F32">0</value>
        <value name="stiffnessCurve" type="Vec4">1 1 1 1</value>
        <value name="stiffnessStrengthCurve" type="Vec4">1 1 1 1</value>
        <value name="stiffnessDampingCurve" type="Vec4">1 1 1 1</value>
        <value name="bendStiffnessCurve" type="Vec4">1 1 1 1</value>
        <value name="interactionStiffnessCurve" type="Vec4">1 1 1 1</value>
        <value name="wind" type="Vec3">0 0 0</value>
        <value name="windNoise" type="F32">0</value>
        <value name="visualizeBones" type="Bool">false</value>
        <value name="visualizeBoundingBox" type="Bool">false</value>
        <value name="visualizeCapsules" type="Bool">false</value>
        <value name="visualizeControlVertices" type="Bool">false</value>
        <value name="visualizeCullSphere" type="Bool">false</value>
        <value name="visualizeDiffuseBone" type="Bool">false</value>
        <value name="visualizeFrames" type="Bool">false</value>
        <value name="visualizeGrowthMesh" type="Bool">false</value>
        <value name="visualizeGuideHairs" type="Bool">false</value>
        <value name="visualizeHairInteractions" type="Bool">false</value>
        <value name="visualizeHairSkips" type="U32">0</value>
        <value name="visualizeLocalPos" type="Bool">false</value>
        <value name="visualizePinConstraints" type="Bool">false</value>
        <value name="visualizeShadingNormals" type="Bool">false</value>
        <value name="visualizeSkinnedGuideHairs" type="Bool">false</value>
        <value name="drawRenderHairs" type="Bool">true</value>
        <value name="enable" type="Bool">true</value>
      </struct>
    </array>
  </struct>
</value>
</NvParameters>'''