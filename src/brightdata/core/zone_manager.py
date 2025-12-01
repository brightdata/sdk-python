"""Zone operations for Bright Data SDK.

Manages zone creation, validation, and listing through the Bright Data API.
"""

import asyncio
import logging
import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from ..exceptions.errors import ZoneError, APIError, AuthenticationError
from ..constants import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_CONFLICT,
    HTTP_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger(__name__)


class ZoneManager:
    """
    Manages Bright Data zones - creation, validation, and listing.

    Uses async/await pattern for non-blocking zone operations.
    Integrates with AsyncEngine for HTTP operations.
    """

    def __init__(self, engine):
        """
        Initialize zone manager.

        Args:
            engine: AsyncEngine instance for making API calls
        """
        self.engine = engine

    async def ensure_required_zones(
        self,
        web_unlocker_zone: str,
        serp_zone: Optional[str] = None,
        browser_zone: Optional[str] = None,
        skip_verification: bool = False,
    ) -> None:
        """
        Check if required zones exist and create them if they don't.

        Important: Only unblocker and SERP zones can be auto-created.
        Browser zones require additional configuration parameters (like "start" value)
        and must be created manually in the Bright Data dashboard.

        Args:
            web_unlocker_zone: Web unlocker zone name (will be created if missing)
            serp_zone: SERP zone name (optional, will be created if missing)
            browser_zone: Browser zone name (NOT auto-created, pass None to skip)

        Raises:
            ZoneError: If zone creation or validation fails
            AuthenticationError: If API token lacks permissions
            APIError: If API request fails
        """
        try:
            logger.info("Checking existing zones...")
            zones = await self._get_zones()
            zone_names = {zone.get("name") for zone in zones}
            logger.info(f"Found {len(zones)} existing zones")

            zones_to_create: List[Tuple[str, str]] = []

            # Check web unlocker zone
            if web_unlocker_zone not in zone_names:
                zones_to_create.append((web_unlocker_zone, "unblocker"))
                logger.info(f"Need to create web unlocker zone: {web_unlocker_zone}")

            # Check SERP zone
            if serp_zone and serp_zone not in zone_names:
                zones_to_create.append((serp_zone, "serp"))
                logger.info(f"Need to create SERP zone: {serp_zone}")

            # Browser zones are intentionally NOT checked here
            # They require additional configuration (like "start" parameter)
            # and must be created manually in the Bright Data dashboard

            if not zones_to_create:
                logger.info("All required zones already exist")
                return

            # Create zones
            for zone_name, zone_type in zones_to_create:
                logger.info(f"Creating zone: {zone_name} (type: {zone_type})")
                try:
                    await self._create_zone(zone_name, zone_type)
                    logger.info(f"Successfully created zone: {zone_name}")
                except AuthenticationError:
                    # Re-raise with clear message - this is a permission issue
                    logger.error(
                        f"Failed to create zone '{zone_name}' due to insufficient permissions"
                    )
                    raise
                except ZoneError as e:
                    # Log and re-raise zone errors
                    logger.error(f"Failed to create zone '{zone_name}': {e}")
                    raise

            # Verify zones were created (unless skipped)
            if not skip_verification:
                try:
                    await self._verify_zones_created([zone[0] for zone in zones_to_create])
                except ZoneError as e:
                    # Log verification failure but don't fail the entire operation
                    logger.warning(
                        f"Zone verification failed: {e}. "
                        f"Zones may have been created but aren't yet visible in the API. "
                        f"Check your dashboard at https://brightdata.com/cp/zones"
                    )
                    # Don't re-raise - zones were likely created successfully
            else:
                logger.info("Skipping zone verification (skip_verification=True)")

        except AuthenticationError as e:
            # Permission errors are critical - show clear message
            logger.error(
                "\n❌ ZONE CREATION BLOCKED: API token lacks required permissions\n"
                f"   Error: {e}\n"
                "   Fix: Update your token permissions at https://brightdata.com/cp/setting/users"
            )
            raise
        except (ZoneError, APIError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error while ensuring zones exist: {e}")
            raise ZoneError(f"Unexpected error during zone creation: {str(e)}")

    async def _get_zones(self) -> List[Dict[str, Any]]:
        """
        Get list of all active zones.

        Returns:
            List of zone dictionaries

        Raises:
            ZoneError: If zone listing fails
            AuthenticationError: If authentication fails
        """
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with self.engine.get("/zone/get_active_zones") as response:
                    if response.status == HTTP_OK:
                        zones = await response.json()
                        return zones or []
                    elif response.status in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
                        error_text = await response.text()
                        raise AuthenticationError(
                            f"Authentication failed ({response.status}): {error_text}"
                        )
                    else:
                        error_text = await response.text()
                        if (
                            attempt < max_retries - 1
                            and response.status >= HTTP_INTERNAL_SERVER_ERROR
                        ):
                            logger.warning(
                                f"Zone list request failed (attempt {attempt + 1}/{max_retries}): "
                                f"{response.status} - {error_text}"
                            )
                            await asyncio.sleep(retry_delay * (1.5**attempt))
                            continue
                        raise ZoneError(f"Failed to list zones ({response.status}): {error_text}")
            except (AuthenticationError, ZoneError):
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Error getting zones (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay * (1.5**attempt))
                    continue
                raise ZoneError(f"Failed to get zones: {str(e)}")

        raise ZoneError("Failed to get zones after all retry attempts")

    async def _create_zone(self, zone_name: str, zone_type: str) -> None:
        """
        Create a new zone in Bright Data.

        Args:
            zone_name: Name for the new zone
            zone_type: Type of zone ('unblocker', 'serp', or 'browser')

        Raises:
            ZoneError: If zone creation fails
            AuthenticationError: If authentication fails
        """
        # Build zone configuration based on type
        if zone_type == "serp":
            plan_config = {"type": "unblocker", "serp": True}
        else:
            plan_config = {"type": zone_type}

        payload = {"plan": plan_config, "zone": {"name": zone_name, "type": zone_type}}

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                async with self.engine.post("/zone", json_data=payload) as response:
                    if response.status in (HTTP_OK, HTTP_CREATED):
                        logger.info(f"Zone creation successful: {zone_name}")
                        return
                    elif response.status == HTTP_CONFLICT:
                        # Zone already exists - this is fine
                        logger.info(f"Zone {zone_name} already exists - this is expected")
                        return
                    else:
                        error_text = await response.text()

                        # Check if error message indicates duplicate zone
                        if (
                            "duplicate" in error_text.lower()
                            or "already exists" in error_text.lower()
                        ):
                            logger.info(f"Zone {zone_name} already exists - this is expected")
                            return

                        # Handle authentication/permission errors
                        if response.status in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
                            # Check for specific permission error
                            if (
                                "permission" in error_text.lower()
                                or "lacks the required" in error_text.lower()
                            ):
                                error_msg = (
                                    f"\n{'='*70}\n"
                                    f"❌ PERMISSION ERROR: Cannot create zone '{zone_name}'\n"
                                    f"{'='*70}\n"
                                    f"Your API key lacks the required permissions for zone creation.\n\n"
                                    f"To fix this:\n"
                                    f"  1. Go to: https://brightdata.com/cp/setting/users\n"
                                    f"  2. Find your API token\n"
                                    f"  3. Enable 'Zone Management' or 'Create Zones' permission\n"
                                    f"  4. Save changes and try again\n\n"
                                    f"API Response: {error_text}\n"
                                    f"{'='*70}\n"
                                )
                                logger.error(error_msg)
                                raise AuthenticationError(
                                    "API key lacks permission to create zones. "
                                    "Update permissions at https://brightdata.com/cp/setting/users"
                                )
                            else:
                                # Generic auth error
                                logger.error(
                                    f"Authentication failed ({response.status}) creating zone '{zone_name}': {error_text}"
                                )
                                raise AuthenticationError(
                                    f"Authentication failed ({response.status}) creating zone '{zone_name}': {error_text}"
                                )

                        # Handle bad request
                        if response.status == HTTP_BAD_REQUEST:
                            raise ZoneError(
                                f"Bad request ({HTTP_BAD_REQUEST}) creating zone '{zone_name}': {error_text}"
                            )

                        # Retry on server errors
                        if (
                            attempt < max_retries - 1
                            and response.status >= HTTP_INTERNAL_SERVER_ERROR
                        ):
                            logger.warning(
                                f"Zone creation failed (attempt {attempt + 1}/{max_retries}): "
                                f"{response.status} - {error_text}"
                            )
                            await asyncio.sleep(retry_delay * (1.5**attempt))
                            continue

                        raise ZoneError(
                            f"Failed to create zone '{zone_name}' ({response.status}): {error_text}"
                        )
            except (AuthenticationError, ZoneError):
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Error creating zone (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay * (1.5**attempt))
                    continue
                raise ZoneError(f"Failed to create zone '{zone_name}': {str(e)}")

        raise ZoneError(f"Failed to create zone '{zone_name}' after all retry attempts")

    async def _verify_zones_created(self, zone_names: List[str]) -> None:
        """
        Verify that zones were successfully created by checking the zones list.

        Note: Zones may take several seconds to appear in the API after creation.
        This method retries multiple times with exponential backoff.

        Args:
            zone_names: List of zone names to verify

        Raises:
            ZoneError: If zone verification fails after all retries
        """
        max_attempts = 5  # Increased from 3 to handle slower propagation
        base_delay = 2.0  # Increased from 1.0 for better reliability

        for attempt in range(max_attempts):
            try:
                # Calculate delay with exponential backoff
                wait_time = base_delay * (1.5**attempt) if attempt > 0 else base_delay
                logger.info(
                    f"Verifying zone creation (attempt {attempt + 1}/{max_attempts}) after {wait_time:.1f}s..."
                )
                await asyncio.sleep(wait_time)

                zones = await self._get_zones()
                existing_zone_names = {zone.get("name") for zone in zones}

                missing_zones = [name for name in zone_names if name not in existing_zone_names]

                if not missing_zones:
                    logger.info(f"All {len(zone_names)} zone(s) verified successfully")
                    return

                if attempt == max_attempts - 1:
                    # Final attempt failed - provide helpful error message
                    error_msg = (
                        f"Zone verification failed after {max_attempts} attempts: "
                        f"zones {missing_zones} not found after creation. "
                        f"The zones may have been created but are not yet visible in the API. "
                        f"Please check your dashboard at https://brightdata.com/cp/zones"
                    )
                    logger.error(error_msg)
                    raise ZoneError(error_msg)

                logger.warning(
                    f"Zones not yet visible: {missing_zones}. "
                    f"Retrying in {base_delay * (1.5 ** attempt):.1f}s..."
                )

            except ZoneError:
                if attempt == max_attempts - 1:
                    raise
                logger.warning(f"Zone verification attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(base_delay * (1.5**attempt))

    async def list_zones(self) -> List[Dict[str, Any]]:
        """
        List all active zones in your Bright Data account.

        Returns:
            List of zone dictionaries with their configurations

        Raises:
            ZoneError: If zone listing fails
            AuthenticationError: If authentication fails

        Example:
            >>> zone_manager = ZoneManager(engine)
            >>> zones = await zone_manager.list_zones()
            >>> print(f"Found {len(zones)} zones")
        """
        try:
            return await self._get_zones()
        except (ZoneError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error listing zones: {e}")
            raise ZoneError(f"Unexpected error while listing zones: {str(e)}")

    async def delete_zone(self, zone_name: str) -> None:
        """
        Delete a zone from your Bright Data account.

        Args:
            zone_name: Name of the zone to delete

        Raises:
            ZoneError: If zone deletion fails
            AuthenticationError: If authentication fails
            APIError: If API request fails

        Example:
            >>> zone_manager = ZoneManager(engine)
            >>> await zone_manager.delete_zone("my_test_zone")
            >>> print(f"Zone 'my_test_zone' deleted successfully")
        """
        if not zone_name or not isinstance(zone_name, str):
            raise ZoneError("Zone name must be a non-empty string")

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to delete zone: {zone_name}")

                # Prepare the payload for zone deletion
                payload = {"zone": zone_name}

                async with self.engine.delete("/zone", json_data=payload) as response:
                    if response.status == HTTP_OK:
                        logger.info(f"Zone '{zone_name}' successfully deleted")
                        return
                    elif response.status in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN):
                        error_text = await response.text()
                        raise AuthenticationError(
                            f"Authentication failed ({response.status}) deleting zone '{zone_name}': {error_text}"
                        )
                    elif response.status == HTTP_BAD_REQUEST:
                        error_text = await response.text()
                        # Check if zone doesn't exist
                        if (
                            "not found" in error_text.lower()
                            or "does not exist" in error_text.lower()
                        ):
                            raise ZoneError(
                                f"Zone '{zone_name}' does not exist or has already been deleted"
                            )
                        raise ZoneError(
                            f"Bad request ({HTTP_BAD_REQUEST}) deleting zone '{zone_name}': {error_text}"
                        )
                    else:
                        error_text = await response.text()

                        # Retry on server errors
                        if (
                            attempt < max_retries - 1
                            and response.status >= HTTP_INTERNAL_SERVER_ERROR
                        ):
                            logger.warning(
                                f"Zone deletion failed (attempt {attempt + 1}/{max_retries}): "
                                f"{response.status} - {error_text}"
                            )
                            await asyncio.sleep(retry_delay * (1.5**attempt))
                            continue

                        raise ZoneError(
                            f"Failed to delete zone '{zone_name}' ({response.status}): {error_text}"
                        )
            except (AuthenticationError, ZoneError):
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Error deleting zone (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    await asyncio.sleep(retry_delay * (1.5**attempt))
                    continue
                raise ZoneError(f"Failed to delete zone '{zone_name}': {str(e)}")

        raise ZoneError(f"Failed to delete zone '{zone_name}' after all retry attempts")
