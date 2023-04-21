templateBone = '''<struct>
        <value name="internalIndex" type="I32">{internalIndex}</value>
        <value name="externalIndex" type="I32">{externalIndex}</value>
        <value name="numMeshReferenced" type="U32">{numMeshReferenced}</value>
        <value name="numRigidBodiesReferenced" type="U32">{numRigidBodiesReferenced}</value>
        <value name="parentIndex" type="I32">{parentIndex}</value>
        <value name="bindPose" type="Mat34">{bindPose}</value>
        <value name="name" type="String">{boneName}</value>
      </struct>'''
      
templateDataPositionNormal = '''<value type="Ref" included="1" className="BufferF32x3" version="0.0" checksum="0x458b554a 0x7ed3e930 0x299ff33 0x9d69c11b">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Vec3">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateDataTangent = '''<value type="Ref" included="1" className="BufferF32x4" version="0.1" checksum="0x80321851 0xa99e95a1 0xd26ec9a8 0x14206b37">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32),z(F32),w(F32)">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateDataColor = '''<value type="Ref" included="1" className="BufferU8x4" version="0.0" checksum="0x8364dd0f 0xbc7542d0 0x1a22d2d2 0x1fc1923">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(U8),y(U8),z(U8),w(U8)">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateDataUV = '''<value type="Ref" included="1" className="BufferF32x2" version="0.0" checksum="0x788349ee 0x95c560e2 0x9633945e 0x8cc784a0">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32)">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateDataBoneIndex = '''<value type="Ref" included="1" className="BufferU16x4" version="0.0" checksum="0x17ce6b83 0x32ba98aa 0xd03f98f6 0x26918369">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(U16),y(U16),z(U16),w(U16)">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateDataBoneWeight = '''<value type="Ref" included="1" className="BufferF32x4" version="0.1" checksum="0x80321851 0xa99e95a1 0xd26ec9a8 0x14206b37">                          
                            <struct name="">
                              <array name="data" size="{numData}" type="Struct" structElements="x(F32),y(F32),z(F32),w(F32)">
                                {arrayData}
                              </array>
                            </struct>
                          </value>'''
                          
templateVertexPositionBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_POSITION</value>
                                <value name="semantic" type="I32">0</value>
                                <value name="id" type="U32">4058349641</value>
                                <value name="format" type="U32">43</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexNormalBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_NORMAL</value>
                                <value name="semantic" type="I32">1</value>
                                <value name="id" type="U32">628990755</value>
                                <value name="format" type="U32">43</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexTangentBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_TANGENT</value>
                                <value name="semantic" type="I32">2</value>
                                <value name="id" type="U32">1201849363</value>
                                <value name="format" type="U32">44</value>
                                <value name="access" type="U32">1</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexColorBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_COLOR</value>
                                <value name="semantic" type="I32">4</value>
                                <value name="id" type="U32">3000270285</value>
                                <value name="format" type="U32">17</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexUVBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_TEXCOORD{numUVBuffer}</value>
                                <value name="semantic" type="I32">{semanticUVBuffer}</value>
                                <value name="id" type="U32">122905935{idEndUVBuffer}</value>
                                <value name="format" type="U32">42</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexBoneIndexBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_BONE_INDEX</value>
                                <value name="semantic" type="I32">9</value>
                                <value name="id" type="U32">284127831</value>
                                <value name="format" type="U32">8</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                              
templateVertexBoneWeightBuffer = '''<struct>
                                <value name="name" type="String">SEMANTIC_BONE_WEIGHT</value>
                                <value name="semantic" type="I32">10</value>
                                <value name="id" type="U32">2091801033</value>
                                <value name="format" type="U32">44</value>
                                <value name="access" type="U32">0</value>
                                <value name="serialize" type="Bool">true</value>
                              </struct>'''
                          
templateGraphicalMesh = '''<value type="Ref" included="1" className="ClothingGraphicalLodParameters" version="0.4" checksum="0x8cf41087 0x1ec73f2e 0x602ad91d 0xdbec5061">      
        <struct name="">
          <array name="platforms" size="0" type="String"></array>
          <value name="lod" type="U32">{numLod}</value>
          <value name="physicalMeshId" type="U32">{physicalMeshId}</value>
          <value name="renderMeshAsset" type="Ref" included="1" className="RenderMeshAssetParameters" version="0.0" checksum="0x119d6f62 0x8d1ff03d 0x19864d20 0x93421fd0">          
            <struct name="">
              <array name="submeshes" size="{numSubMeshes}" type="Ref">
                {subMeshes}
              </array>
              <array name="materialNames" size="{numSubMeshes}" type="String">
                {materials}
              </array>
              <array name="partBounds" size="1" type="Bounds3">
                {partBounds}
              </array>
              <value name="textureUVOrigin" type="U32">2</value>
              <value name="boneCount" type="U32">{numUsedBones}</value>
              <value name="deleteStaticBuffersAfterUse" type="Bool">false</value>
              <value name="isReferenced" type="Bool">true</value>
            </struct>
          </value>
          <array name="immediateClothMap" size="{numImmediateClothMap}" type="U32">
            {immediateClothMap}
          </array>
          <array name="skinClothMapB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="skinClothMap" size="{numSkinClothMap}" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)">
            {skinClothMap}
          </array>
          <value name="skinClothMapThickness" type="F32">1</value>
          <value name="skinClothMapOffset" type="F32">{skinClothMapOffset}</value>
          <array name="tetraMap" size="0" type="Struct" structElements="vertexBary(Vec3),tetraIndex0(U32),normalBary(Vec3)"></array>
          <value name="renderMeshAssetSorting" type="U32">1</value>
          <array name="physicsSubmeshPartitioning" size="{numPhysicsSubmeshPartitioning}" type="Struct" structElements="graphicalSubmesh(U32),physicalSubmesh(U32),numSimulatedVertices(U32),numSimulatedVerticesAdditional(U32),numSimulatedIndices(U32)">
            {physicsSubmeshPartitioning}
          </array>
        </struct>
      </value>'''
      
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

templateSimulationMaterial = '''<struct>
            <value name="materialName" type="String">{simulationMaterialName}</value>
            <value name="verticalStretchingStiffness" type="F32">1</value>
            <value name="horizontalStretchingStiffness" type="F32">1</value>
            <value name="bendingStiffness" type="F32">0.5</value>
            <value name="shearingStiffness" type="F32">0.5</value>
            <value name="zeroStretchStiffness" type="F32">0</value>
            <value name="tetherStiffness" type="F32">1</value>
            <value name="tetherLimit" type="F32">1</value>
            <value name="orthoBending" type="Bool">false</value>
            <struct name="verticalStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="horizontalStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="bendingStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <struct name="shearingStiffnessScaling">
              <value name="compressionRange" type="F32">1</value>
              <value name="stretchRange" type="F32">1</value>
              <value name="scale" type="F32">0.5</value>
            </struct>
            <value name="damping" type="F32">0.5</value>
            <value name="stiffnessFrequency" type="F32">100</value>
            <value name="drag" type="F32">0</value>
            <value name="comDamping" type="Bool">false</value>
            <value name="friction" type="F32">0.5</value>
            <value name="massScale" type="F32">25</value>
            <value name="solverIterations" type="U32">5</value>
            <value name="solverFrequency" type="F32">250</value>
            <value name="gravityScale" type="F32">1</value>
            <value name="inertiaScale" type="F32">0.5</value>
            <value name="hardStretchLimitation" type="F32">0</value>
            <value name="maxDistanceBias" type="F32">0</value>
            <value name="hierarchicalSolverIterations" type="U32">0</value>
            <value name="selfcollisionThickness" type="F32">0</value>
            <value name="selfcollisionSquashScale" type="F32">0</value>
            <value name="selfcollisionStiffness" type="F32">0</value>
          </struct>'''
          
templatePhysicalMesh = '''<value type="Ref" included="1" className="ClothingPhysicalMeshParameters" version="0.10" checksum="0xcffdb608 0x34772e05 0xb720e9cd 0xf962cbf8">      
        <struct name="">
          <struct name="physicalMesh">
            <value name="numVertices" type="U32">{numVertices_PhysicalMesh}</value>
            <value name="numIndices" type="U32">{numFaceIndices_PhysicalMesh}</value>
            <value name="numBonesPerVertex" type="U32">4</value>
            <array name="vertices" size="{numVertices_PhysicalMesh}" type="Vec3">
              {vertices_PhysicalMesh}
            </array>
            <array name="normals" size="{numVertices_PhysicalMesh}" type="Vec3">
              {normals_PhysicalMesh}
            </array>
            <array name="skinningNormals" size="{numVertices_PhysicalMesh}" type="Vec3">
              {skinningNormals_PhysicalMesh}
            </array>
            <array name="constrainCoefficients" size="{numVertices_PhysicalMesh}" type="Struct" structElements="maxDistance(F32),collisionSphereRadius(F32),collisionSphereDistance(F32)">
              {constrainCoefficients_PhysicalMesh}
            </array>
            <array name="boneIndices" size="{numBoneIndices_PhysicalMesh}" type="U16">
              {boneIndices_PhysicalMesh}
            </array>
            <array name="boneWeights" size="{numBoneIndices_PhysicalMesh}" type="F32">
              {boneWeights_PhysicalMesh}
            </array>
            <array name="optimizationData" size="{numOptimizationData}" type="U8">
              {optimizationData}
            </array>
            <value name="hasNegativeBackstop" type="Bool">false</value>
            <value name="isClosed" type="Bool">false</value>
            <array name="indices" size="{numFaceIndices_PhysicalMesh}" type="U32">
              {faceIndices_PhysicalMesh}
            </array>
            <value name="maximumMaxDistance" type="F32">{maximumMaxDistance}</value>
            <value name="physicalMeshSorting" type="U32">1</value>
            <value name="shortestEdgeLength" type="F32">{shortestEdgeLength}</value>
            <value name="averageEdgeLength" type="F32">{averageEdgeLength}</value>
            <value name="isTetrahedralMesh" type="Bool">false</value>
            <value name="flipNormals" type="Bool">false</value>
          </struct>
          <array name="submeshes" size="{numSubMeshes_PhysicalMesh}" type="Struct" structElements="numIndices(U32),numVertices(U32),numMaxDistance0Vertices(U32)">
            {subMeshes_PhysicalMesh}
          </array>
          <array name="physicalLods" size="{numPhysicalLods}" type="Struct" structElements="costWithoutIterations(U32),submeshId(U32),solverIterationScale(F32),maxDistanceReduction(F32)">
            {physicalLods}
          </array>
          <array name="transitionUpB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="transitionUp" size="{numTransitionUp}" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)">
            {transitionUp}
          </array>
          <value name="transitionUpThickness" type="F32">{transitionUpThickness}</value>
          <value name="transitionUpOffset" type="F32">{transitionUpOffset}</value>
          <array name="transitionDownB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="transitionDown" size="{numTransitionDown}" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)">
            {transitionDown}
          </array>
          <value name="transitionDownThickness" type="F32">{transitionDownThickness}</value>
          <value name="transitionDownOffset" type="F32">{transitionDownOffset}</value>
          <value name="referenceCount" type="U32">1</value>
        </struct>
      </value>'''
      
templateSubMesh = '''<value type="Ref" included="1" className="SubmeshParameters" version="0.1" checksum="0xb2b4f308 0x5f4b8da6 0x4d45daeb 0xbfc7d9b0">                
                  <struct name="">
                    <value name="vertexBuffer" type="Ref" included="1" className="VertexBufferParameters" version="0.1" checksum="0x14ae7314 0xe50741cb 0x15eb480c 0x63f6c571">                    
                      <struct name="">
                        <value name="vertexCount" type="U32">{numVertices}</value>
                        <value name="vertexFormat" type="Ref" included="1" className="VertexFormatParameters" version="0.0" checksum="0xa7c1ed95 0x570ed2b1 0x55717659 0x9951d139">                        
                          <struct name="">
                            <value name="winding" type="U32">2</value>
                            <value name="hasSeparateBoneBuffer" type="Bool">true</value>
                            <array name="bufferFormats" size="{numBuffers}" type="Struct">
                              {bufferFormats}
                            </array>
                          </struct>
                        </value>
                        <array name="buffers" size="{numBuffers}" type="Ref">
                          {bufferData}
                        </array>
                      </struct>
                    </value>
                    <array name="indexBuffer" size="{numIndices}" type="U32">
                      {faceIndices}
                    </array>
                    <array name="vertexPartition" size="2" type="U32">
                      {vertexPartition}
                    </array>
                    <array name="indexPartition" size="2" type="U32">
                      {indexPartition}
                    </array>
                    <array name="smoothingGroups" size="0" type="U32"></array>
                  </struct>
                </value>'''