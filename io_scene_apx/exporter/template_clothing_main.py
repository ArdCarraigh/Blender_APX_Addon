templateClothingMain = '''<!DOCTYPE NxParameters>
<NxParameters numObjects="1" version="1.0" >
<value name="" type="Ref" className="ClothingAssetParameters" version="0.13" checksum="0x1c07d2c0 0xa436dad5 0xb2c1e2a5 0xcf467a82">
  <struct name="">
    <array name="physicalMeshes" size="{numPhysicalMeshes}" type="Ref">
	  {physicalMeshes}
    </array>
    <array name="graphicalLods" size="{numGraphicalMeshes}" type="Ref">
	  {graphicalMeshes}
    </array>
    <struct name="simulation">
      <value name="hierarchicalLevels" type="U32">0</value>
      <value name="thickness" type="F32">0.00999999978</value>
      <value name="virtualParticleDensity" type="F32">0</value>
      <value name="gravityDirection" type="Vec3">0 0 -1</value>
      <value name="sleepLinearVelocity" type="F32">0</value>
      <value name="disableCCD" type="Bool">true</value>
      <value name="untangling" type="Bool">false</value>
      <value name="twowayInteraction" type="Bool">false</value>
      <value name="restLengthScale" type="F32">1</value>
    </struct>
    <array name="bones" size="{numBones}" type="Struct">
      {bones}
    </array>
    <value name="bonesReferenced" type="U32">{bonesReferenced}</value>
    <value name="bonesReferencedByMesh" type="U32">{bonesReferencedByMesh}</value>
    <value name="rootBoneIndex" type="U32">{rootBoneIndex}</value>
    <array name="boneActors" size="{numBoneActors}" type="Struct" structElements="boneIndex(I32),convexVerticesStart(U32),convexVerticesCount(U32),capsuleRadius(F32),capsuleHeight(F32),localPose(Mat34)">
      {boneActors}
    </array>
    <array name="boneVertices" size="0" type="Vec3"></array>
    <array name="boneSpheres" size="{numBoneSpheres}" type="Struct" structElements="boneIndex(I32),radius(F32),localPos(Vec3)">
	  {boneSpheres}
	</array>
    <array name="boneSphereConnections" size="{numBoneSphereConnections}" type="U16">
	  {boneSphereConnections}
	</array>
    <array name="bonePlanes" size="0" type="Struct" structElements="boneIndex(I32),n(Vec3),d(F32)"></array>
    <array name="collisionConvexes" size="0" type="U32"></array>
    <array name="cookedData" size="0" type="Struct">
    </array>
    <value name="boundingBox" type="Bounds3">{boundingBox}</value>
    <value name="materialLibrary" type="Ref" included="1" className="ClothingMaterialLibraryParameters" version="0.13" checksum="0x81ce711f 0x95e15fb3 0xfa092d04 0xcd72e3c8">    
      <struct name="">
        <array name="materials" size="{numGraphicalMeshes}" type="Struct">
          {simulationMaterials}
        </array>
      </struct>
    </value>
    <value name="materialIndex" type="U32">0</value>
    <value name="interCollisionChannels" type="U32">0</value>
    <value name="toolString" type="String">PhysX/APEX for Max 3.0.11027.19442:CL 16932366 Win64 (Apex 1.3, CL 17153006, PROFILE RELEASE) (PhysX 3.3) Apex Build Time: 16:39:34, Sun Jun 29, 2014</value>
  </struct>
</value>
</NxParameters>'''
