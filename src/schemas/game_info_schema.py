from enum import StrEnum
from typing import Union, Any

from pydantic import BaseModel, Field, AnyUrl, AwareDatetime, FutureDatetime, computed_field


class ImageType(StrEnum):
    OFFER_IMAGE_WIDE = "OfferImageWide"
    OFFER_IMAGE_TALL = "OfferImageTall"
    THUMBNAIL = "Thumbnail"
    HERO_CAROUSEL_VIDEO = "heroCarouselVideo"
    FEATURED_MEDIA = "featuredMedia"
    GALLERY_IMAGE = "GalleryImage"
    DIESEL_STORE_FRONT_WIDE = "DieselStoreFrontWide"
    VAULT_CLOSED = "VaultClosed"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.UNKNOWN


class KeyImageSchema(BaseModel):
    type: ImageType
    url: AnyUrl


class SellerSchema(BaseModel):
    id: str
    name: str


class PageSchema(BaseModel):
    page_slug: str = Field(alias="pageSlug")
    page_type: str = Field(alias="pageType")


class CatalogNsSchema(BaseModel):
    mappings: list[PageSchema]


class TotalPriceSchema(BaseModel):
    discount_price: int = Field(ge=0, alias="discountPrice")
    original_price: int = Field(ge=0, alias="originalPrice")
    discount: int = Field(ge=0)


class PriceSchema(BaseModel):
    total_price: TotalPriceSchema = Field(alias="totalPrice")


class DiscountSettingSchema(BaseModel):
    discount_type: str = Field(alias="discountType")
    discount_percentage: int = Field(ge=0, alias="discountPercentage")


class PromotionalOfferSchema(BaseModel):
    start_date: AwareDatetime = Field(alias="startDate")
    end_date: Union[AwareDatetime, FutureDatetime] = Field(alias="endDate")
    discount_setting: DiscountSettingSchema = Field(alias="discountSetting")


class PromotionalOffersListSchema(BaseModel):
    promotional_offers: list[PromotionalOfferSchema] = Field(alias="promotionalOffers")


class PromotionsSchema(BaseModel):
    promotional_offers: list[PromotionalOffersListSchema] | None = Field(alias="promotionalOffers")
    upcoming_promotional_offers: list[PromotionalOffersListSchema] | None = Field(alias="upcomingPromotionalOffers")


class GameInfoSchema(BaseModel):
    title: str
    id: str
    description: str
    key_images: list[KeyImageSchema] = Field(alias="keyImages")
    seller: SellerSchema
    offer_mappings: list[PageSchema] = Field(alias="offerMappings")
    catalog_ns: CatalogNsSchema = Field(alias="catalogNs")
    price: PriceSchema
    promotions: PromotionsSchema | None

    @computed_field
    @property
    def free_offer(self) -> PromotionalOfferSchema | None:
        def find_free_offer(offers_list: PromotionalOffersListSchema) -> PromotionalOfferSchema | None:
            for offer in offers_list.promotional_offers:
                if (
                    offer.discount_setting.discount_type == "PERCENTAGE"
                    and offer.discount_setting.discount_percentage == 0
                ):
                    return offer
            return None

        if not self.promotions:
            return None

        if self.promotions.promotional_offers:
            free_offer = find_free_offer(self.promotions.promotional_offers[0])
            if free_offer:
                return free_offer
        if self.promotions.upcoming_promotional_offers:
            free_offer = find_free_offer(self.promotions.upcoming_promotional_offers[0])
            return free_offer

        return None

    @computed_field
    @property
    def wide_img_url(self) -> str | None:
        try:
            url = str(next(filter(lambda x: x.type == ImageType.OFFER_IMAGE_WIDE, self.key_images)).url)
        except StopIteration:
            return None
        else:
            return url
