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