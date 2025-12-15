import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useTranslation } from 'react-i18next'
import { fieldService } from '@/services/fieldService'
import { MapPin, Droplets, Leaf, Loader2, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

export function FieldForm() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    area: '',
    soilPh: '',
    soilN: '',
    soilP: '',
    soilK: '',
    lastCrop: '',
    irrigationAvailable: false,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const field = await fieldService.createField(formData)
      console.log("field Created for :", `${field.id}`)
      navigate(`/recommendations/${field.id}`)
    } catch (error) {
      console.error('Error creating field:', error)
      alert('Failed to create field. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="w-4 h-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">{t('fieldForm.title')}</h1>
          <p className="text-muted-foreground mt-1">{t('fieldForm.description')}</p>
        </div>
      </div>

      <Card className="border-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-primary" />
            Field Information
          </CardTitle>
          <CardDescription>Enter your field details to get personalized crop recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="latitude" className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {t('fieldForm.latitude')}
                  </Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="any"
                    required
                    placeholder="e.g., 28.6139"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    className="transition-all focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="longitude" className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {t('fieldForm.longitude')}
                  </Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="any"
                    required
                    placeholder="e.g., 77.2090"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    className="transition-all focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="area">{t('fieldForm.area')} (hectares)</Label>
                <Input
                  id="area"
                  type="number"
                  step="any"
                  required
                  placeholder="Enter field area"
                  value={formData.area}
                  onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                  className="transition-all focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="border-t pt-6">
              <CardTitle className="text-lg mb-4 flex items-center gap-2">
                <Leaf className="w-5 h-5 text-primary" />
                Soil Properties
              </CardTitle>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="soilPh">pH Level</Label>
                    <Input
                      id="soilPh"
                      type="number"
                      step="any"
                      min="0"
                      max="14"
                      placeholder="0-14"
                      value={formData.soilPh}
                      onChange={(e) => setFormData({ ...formData, soilPh: e.target.value })}
                      className="transition-all focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="soilN">Nitrogen (N) kg/ha</Label>
                    <Input
                      id="soilN"
                      type="number"
                      step="any"
                      placeholder="N content"
                      value={formData.soilN}
                      onChange={(e) => setFormData({ ...formData, soilN: e.target.value })}
                      className="transition-all focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="soilP">Phosphorus (P) kg/ha</Label>
                    <Input
                      id="soilP"
                      type="number"
                      step="any"
                      placeholder="P content"
                      value={formData.soilP}
                      onChange={(e) => setFormData({ ...formData, soilP: e.target.value })}
                      className="transition-all focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="soilK">Potassium (K) kg/ha</Label>
                  <Input
                    id="soilK"
                    type="number"
                    step="any"
                    placeholder="K content"
                    value={formData.soilK}
                    onChange={(e) => setFormData({ ...formData, soilK: e.target.value })}
                    className="transition-all focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            <div className="border-t pt-6">
              <CardTitle className="text-lg mb-4 flex items-center gap-2">
                <Droplets className="w-5 h-5 text-primary" />
                Additional Information
              </CardTitle>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="lastCrop">{t('fieldForm.lastCrop')}</Label>
                  <Input
                    id="lastCrop"
                    placeholder="Previous crop name"
                    value={formData.lastCrop}
                    onChange={(e) => setFormData({ ...formData, lastCrop: e.target.value })}
                    className="transition-all focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div className="flex items-center space-x-3 p-4 rounded-lg border bg-muted/50">
                  <input
                    type="checkbox"
                    id="irrigation"
                    checked={formData.irrigationAvailable}
                    onChange={(e) => setFormData({ ...formData, irrigationAvailable: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <Label htmlFor="irrigation" className="cursor-pointer flex-1">
                    {t('fieldForm.irrigationAvailable')}
                  </Label>
                </div>
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <Link to="/" className="flex-1">
                <Button type="button" variant="outline" className="w-full">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" className="flex-1" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    {t('common.loading')}
                  </>
                ) : (
                  t('fieldForm.submit')
                )}
              </Button>
            </div>
        </form>
      </CardContent>
    </Card>
    </div>
  )
}

