import httpx
from typing import List, Dict, Optional, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class InfernoClient:
    def __init__(self):
        self.base_url = settings.inferno_validator_url
        self.client: Optional[httpx.AsyncClient] = None
        self._loaded_igs: Dict[str, Dict[str, Any]] = {}
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=60.0)
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def validate_resource(self, resource: str, profiles: List[str]) -> Dict[str, Any]:
        """
        Validate a FHIR resource against specified profiles.
        """
        client = await self._get_client()
        
        profile_param = ",".join(profiles) if profiles else ""
        
        url = f"{self.base_url}/validate"
        if profile_param:
            url += f"?profile={profile_param}"
        
        try:
            response = await client.post(
                url,
                content=resource,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Validation failed with status {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Validation request failed: {str(e)}")
            raise
    
    async def get_profiles(self) -> List[str]:
        """
        Get list of all available profiles.
        """
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.base_url}/profiles")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get profiles: {str(e)}")
            return []
    
    async def get_profiles_by_ig(self) -> Dict[str, List[str]]:
        """
        Get profiles grouped by Implementation Guide.
        """
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.base_url}/profiles-by-ig")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get profiles by IG: {str(e)}")
            return {}
    
    async def get_igs(self) -> Dict[str, Any]:
        """
        Get list of loaded Implementation Guides.
        """
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.base_url}/igs")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get IGs: {str(e)}")
            return {}
    
    async def load_ig_by_id(self, package_id: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Load an Implementation Guide by NPM package ID.
        """
        client = await self._get_client()
        
        url = f"{self.base_url}/igs/{package_id}"
        if version:
            url += f"?version={version}"
        
        try:
            response = await client.put(url)
            response.raise_for_status()
            result = response.json()
            
            self._loaded_igs[package_id] = result
            logger.info(f"Successfully loaded IG: {package_id}#{version or 'latest'}")
            
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to load IG {package_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to load IG {package_id}: {str(e)}")
            raise
    
    async def upload_custom_ig(self, package_data: bytes) -> Dict[str, Any]:
        """
        Upload a custom Implementation Guide package.tgz.
        """
        client = await self._get_client()
        
        try:
            response = await client.post(
                f"{self.base_url}/igs",
                content=package_data,
                headers={"Content-Encoding": "gzip"}
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Successfully uploaded custom IG: {result.get('id')}")
            
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to upload custom IG: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to upload custom IG: {str(e)}")
            raise
    
    async def get_version(self) -> Dict[str, str]:
        """
        Get version information from the validator service.
        """
        client = await self._get_client()
        
        try:
            response = await client.get(f"{self.base_url}/version")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get version: {str(e)}")
            return {}
    
    async def load_default_igs(self):
        """
        Load default Implementation Guides on startup.
        """
        default_igs = settings.default_igs_list
        
        for ig_spec in default_igs:
            try:
                if '#' in ig_spec:
                    package_id, version = ig_spec.split('#', 1)
                else:
                    package_id = ig_spec
                    version = None
                
                logger.info(f"Loading default IG: {package_id}#{version or 'latest'}")
                await self.load_ig_by_id(package_id, version)
            except Exception as e:
                logger.warning(f"Failed to load default IG {ig_spec}: {str(e)}")


inferno_client = InfernoClient()
