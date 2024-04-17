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
        <value name="densityTexture" type="String">{densityTexture}</value>
        <value name="rootColorTexture" type="String">{rootColorTexture}</value>
        <value name="tipColorTexture" type="String">{tipColorTexture}</value>
        <value name="widthTexture" type="String">{widthTexture}</value>
        <value name="rootWidthTexture" null="1" type="String">{rootWidthTexture}</value>
        <value name="tipWidthTexture" null="1" type="String">{tipWidthTexture}</value>
        <value name="stiffnessTexture" type="String">{stiffnessTexture}</value>
        <value name="rootStiffnessTexture" type="String">{rootStiffnessTexture}</value>
        <value name="clumpScaleTexture" type="String">{clumpScaleTexture}</value>
        <value name="clumpRoundnessTexture" type="String">{clumpRoundnessTexture}</value>
        <value name="clumpNoiseTexture" null="1" type="String">{clumpNoiseTexture}</value>
        <value name="waveScaletexture" type="String">{waveScaletexture}</value>
        <value name="waveFreqTexture" type="String">{waveFreqTexture}</value>
        <value name="strandTexture" type="String">{strandTexture}</value>
        <value name="lengthTexture" type="String">{lengthTexture}</value>
        <value name="specularTexture" type="String">{specularTexture}</value>
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
        <array name="faceUVs" size="{n_faceIndices}" type="Vec2">
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
        <array name="boneParents" size="{numBones}" type="I32">
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
        <array name="pinConstraints" size="{numPinConstraints}" type="Struct" structElements="boneSphereIndex(I32),boneSphereRadius(F32),boneSphereLocalPos(Vec3),pinStiffness(F32),influenceFallOff(F32),useDynamicPin(Bool),doLra(Bool),useStiffnessPin(Bool),influenceFallOffCurve(Vec4)">
            {pinConstraints}
        </array>
        <value name="sceneUnit" type="F32">1</value>
        <value name="upAxis" type="U32">2</value>
        <value name="handedness" type="U32">1</value>
    </struct>
</value>
<value name="" type="Ref" className="HairInstanceDescriptor" version="1.1" checksum="">
  <struct name="">
    <array name="materials" size="4" type="Struct">
      <struct>
        <value name="name" null="1" type="String">{matName}</value>
        <value name="densityTextureChan" type="U32">{densityTextureChan}</value>
        <value name="widthTextureChan" type="U32">{widthTextureChan}</value>
        <value name="rootWidthTextureChan" type="U32">{rootWidthTextureChan}</value>
        <value name="tipWidthTextureChan" type="U32">{tipWidthTextureChan}</value>
        <value name="clumpScaleTextureChan" type="U32">{clumpScaleTextureChan}</value>
        <value name="clumpNoiseTextureChan" type="U32">{clumpNoiseTextureChan}</value>
        <value name="clumpRoundnessTextureChan" type="U32">{clumpRoundnessTextureChan}</value>
        <value name="waveScaleTextureChan" type="U32">{waveScaleTextureChan}</value>
        <value name="waveFreqTextureChan" type="U32">{waveFreqTextureChan}</value>
        <value name="lengthTextureChan" type="U32">{lengthTextureChan}</value>
        <value name="stiffnessTextureChan" type="U32">{stiffnessTextureChan}</value>
        <value name="rootStiffnessTextureChan" type="U32">{rootStiffnessTextureChan}</value>
        <value name="splineMultiplier" type="U32">{splineMultiplier}</value>
        <value name="assetType" type="U32">{assetType}</value>
        <value name="assetPriority" type="U32">{assetPriority}</value>
        <value name="assetGroup" type="U32">{assetGroup}</value>
        <value name="width" type="F32">{width}</value>
        <value name="widthNoise" type="F32">{widthNoise}</value>
        <value name="clumpNoise" type="F32">{clumpNoise}</value>
        <value name="clumpNumSubclumps" type="U32">{clumpNumSubclumps}</value>
        <value name="clumpRoundness" type="F32">{clumpRoundness}</value>
        <value name="clumpScale" type="F32">{clumpScale}</value>
        <value name="clumpPerVertex" type="Bool">{clumpPerVertex}</value>
        <value name="density" type="F32">{density}</value>
        <value name="lengthNoise" type="F32">{lengthNoise}</value>
        <value name="lengthScale" type="F32">{lengthScale}</value>
        <value name="widthRootScale" type="F32">{widthRootScale}</value>
        <value name="widthTipScale" type="F32">{widthTipScale}</value>
        <value name="waveRootStraighten" type="F32">{waveRootStraighten}</value>
        <value name="waveScale" type="F32">{waveScale}</value>
        <value name="waveScaleNoise" type="F32">{waveScaleNoise}</value>
        <value name="waveFreq" type="F32">{waveFreq}</value>
        <value name="waveFreqNoise" type="F32">{waveFreqNoise}</value>
        <value name="waveScaleStrand" type="F32">{waveScaleStrand}</value>
        <value name="waveScaleClump" type="F32">{waveScaleClump}</value>
        <value name="enableDistanceLOD" type="Bool">{enableDistanceLOD}</value>
        <value name="distanceLODStart" type="F32">{distanceLODStart}</value>
        <value name="distanceLODEnd" type="F32">{distanceLODEnd}</value>
        <value name="distanceLODFadeStart" type="F32">{distanceLODFadeStart}</value>
        <value name="distanceLODDensity" type="F32">{distanceLODDensity}</value>
        <value name="distanceLODWidth" type="F32">{distanceLODWidth}</value>
        <value name="enableDetailLOD" type="Bool">{enableDetailLOD}</value>
        <value name="detailLODStart" type="F32">{detailLODStart}</value>
        <value name="detailLODEnd" type="F32">{detailLODEnd}</value>
        <value name="detailLODDensity" type="F32">{detailLODDensity}</value>
        <value name="detailLODWidth" type="F32">{detailLODWidth}</value>
        <value name="colorizeLODOption" type="U32">{colorizeLODOption}</value>
        <value name="useViewfrustrumCulling" type="Bool">{useViewfrustrumCulling}</value>
        <value name="useBackfaceCulling" type="Bool">{useBackfaceCulling}</value>
        <value name="backfaceCullingThreshold" type="F32">{backfaceCullingThreshold}</value>
        <value name="usePixelDensity" type="Bool">{usePixelDensity}</value>
        <value name="alpha" type="F32">{alpha}</value>
        <value name="strandBlendScale" type="F32">{strandBlendScale}</value>
        <value name="baseColor" type="Vec4">{baseColor}</value>
        <value name="diffuseBlend" type="F32">{diffuseBlend}</value>
        <value name="diffuseScale" type="F32">{diffuseScale}</value>
        <value name="diffuseHairNormalWeight" type="F32">{diffuseHairNormalWeight}</value>
        <value name="diffuseBoneIndex" type="U32">{diffuseBoneIndex}</value>
        <value name="diffuseBoneLocalPos" type="Vec3">{diffuseBoneLocalPos}</value>
        <value name="diffuseNoiseFreqU" type="F32">{diffuseNoiseFreqU}</value>
        <value name="diffuseNoiseFreqV" type="F32">{diffuseNoiseFreqV}</value>
        <value name="diffuseNoiseScale" type="F32">{diffuseNoiseScale}</value>
        <value name="diffuseNoiseGain" type="F32">{diffuseNoiseGain}</value>
        <value name="textureBrightness" type="F32">{textureBrightness}</value>
        <value name="diffuseColor" type="Vec4">{diffuseColor}</value>
        <value name="rootColor" type="Vec4">{rootColor}</value>
        <value name="tipColor" type="Vec4">{tipColor}</value>
        <value name="glintStrength" type="F32">{glintStrength}</value>
        <value name="glintCount" type="F32">{glintCount}</value>
        <value name="glintExponent" type="F32">{glintExponent}</value>
        <value name="rootAlphaFalloff" type="F32">{rootAlphaFalloff}</value>
        <value name="rootTipColorWeight" type="F32">{rootTipColorWeight}</value>
        <value name="rootTipColorFalloff" type="F32">{rootTipColorFalloff}</value>
        <value name="shadowSigma" type="F32">{shadowSigma}</value>
        <value name="specularColor" type="Vec4">{specularColor}</value>
        <value name="specularPrimary" type="F32">{specularPrimary}</value>
        <value name="specularNoiseScale" type="F32">{specularNoiseScale}</value>
        <value name="specularEnvScale" type="F32">{specularEnvScale}</value>
        <value name="specularPrimaryBreakup" type="F32">{specularPrimaryBreakup}</value>
        <value name="specularSecondary" type="F32">{specularSecondary}</value>
        <value name="specularSecondaryOffset" type="F32">{specularSecondaryOffset}</value>
        <value name="specularPowerPrimary" type="F32">{specularPowerPrimary}</value>
        <value name="specularPowerSecondary" type="F32">{specularPowerSecondary}</value>
        <value name="strandBlendMode" type="U32">{strandBlendMode}</value>
        <value name="useTextures" type="Bool">{useTextures}</value>
        <value name="useShadows" type="Bool">{useShadows}</value>
        <value name="shadowDensityScale" type="F32">{shadowDensityScale}</value>
        <value name="castShadows" type="Bool">{castShadows}</value>
        <value name="receiveShadows" type="Bool">{receiveShadows}</value>
        <value name="backStopRadius" type="F32">{backStopRadius}</value>
        <value name="bendStiffness" type="F32">{bendStiffness}</value>
        <value name="interactionStiffness" type="F32">{interactionStiffness}</value>
        <value name="pinStiffness" type="F32">{pinStiffness}</value>
        <value name="collisionOffset" type="F32">{collisionOffset}</value>
        <value name="useCollision" type="Bool">{useCollision}</value>
        <value name="useDynamicPin" type="Bool">{useDynamicPin}</value>
        <value name="damping" type="F32">{damping}</value>
        <value name="friction" type="F32">{friction}</value>
        <value name="massScale" type="F32">{massScale}</value>
        <value name="gravity" type="Vec3">{gravity}</value>
        <value name="inertiaScale" type="F32">{inertiaScale}</value>
        <value name="inertiaLimit" type="F32">{inertiaLimit}</value>
        <value name="rootStiffness" type="F32">{rootStiffness}</value>
        <value name="tipStiffness" type="F32">{tipStiffness}</value>
        <value name="simulate" type="Bool">{simulate}</value>
        <value name="stiffness" type="F32">{stiffness}</value>
        <value name="stiffnessStrength" type="F32">{stiffnessStrength}</value>
        <value name="stiffnessDamping" type="F32">{stiffnessDamping}</value>
        <value name="stiffnessCurve" type="Vec4">{stiffnessCurve}</value>
        <value name="stiffnessStrengthCurve" type="Vec4">{stiffnessStrengthCurve}</value>
        <value name="stiffnessDampingCurve" type="Vec4">{stiffnessDampingCurve}</value>
        <value name="bendStiffnessCurve" type="Vec4">{bendStiffnessCurve}</value>
        <value name="interactionStiffnessCurve" type="Vec4">{interactionStiffnessCurve}</value>
        <value name="wind" type="Vec3">{wind}</value>
        <value name="windNoise" type="F32">{windNoise}</value>
        <value name="visualizeBones" type="Bool">{visualizeBones}</value>
        <value name="visualizeBoundingBox" type="Bool">{visualizeBoundingBox}</value>
        <value name="visualizeCapsules" type="Bool">{visualizeCapsules}</value>
        <value name="visualizeControlVertices" type="Bool">{visualizeControlVertices}</value>
        <value name="visualizeCullSphere" type="Bool">{visualizeCullSphere}</value>
        <value name="visualizeDiffuseBone" type="Bool">{visualizeDiffuseBone}</value>
        <value name="visualizeFrames" type="Bool">{visualizeFrames}</value>
        <value name="visualizeGrowthMesh" type="Bool">{visualizeGrowthMesh}</value>
        <value name="visualizeGuideHairs" type="Bool">{visualizeGuideHairs}</value>
        <value name="visualizeHairInteractions" type="Bool">{visualizeHairInteractions}</value>
        <value name="visualizeHairSkips" type="U32">{visualizeHairSkips}</value>
        <value name="visualizeLocalPos" type="Bool">{visualizeLocalPos}</value>
        <value name="visualizePinConstraints" type="Bool">{visualizePinConstraints}</value>
        <value name="visualizeShadingNormals" type="Bool">{visualizeShadingNormals}</value>
        <value name="visualizeSkinnedGuideHairs" type="Bool">{visualizeSkinnedGuideHairs}</value>
        <value name="drawRenderHairs" type="Bool">{drawRenderHairs}</value>
        <value name="enable" type="Bool">{enable}</value>
      </struct>
    </array>
  </struct>
</value>
</NvParameters>'''